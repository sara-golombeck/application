#!/bin/bash

# E2E Tests for Playlists API - Jenkins Pipeline Compatible
# Professional test suite for CI/CD integration

set -e

# Configuration
BASE_URL="http://localhost"
HEALTH_ENDPOINT="${BASE_URL}/health"
API_ENDPOINT="${BASE_URL}/api/playlists"

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Simple logging without colors for professional output

# Logging functions
log_test() {
    echo "=== TEST: $1 ==="
    ((TOTAL_TESTS++))
}

log_pass() {
    echo "PASS: $1"
    ((PASSED_TESTS++))
}

log_fail() {
    echo "FAIL: $1"
    ((FAILED_TESTS++))
}

log_info() {
    echo "INFO: $1"
}

# Wait for service to be available
wait_for_service() {
    log_info "Waiting for service to be ready..."
    
    for i in {1..30}; do
        if curl -s -f "$HEALTH_ENDPOINT" >/dev/null 2>&1; then
            log_pass "Service is ready after ${i} attempts"
            return 0
        fi
        echo "Waiting... attempt $i/30"
        sleep 2
    done
    
    log_fail "Service did not become ready within timeout"
    return 1
}

# Test 1: Health Check
test_health_check() {
    log_test "Health Check"
    
    local response=$(curl -s -w "\n%{http_code}" "$HEALTH_ENDPOINT" || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        log_pass "Health check endpoint returns 200"
    else
        log_fail "Health check failed with status: $status_code"
        return 1
    fi
}

# Test 2: API Landing Page
test_landing_page() {
    log_test "API Landing Page"
    
    local response=$(curl -s -w "\n%{http_code}" "$BASE_URL/" || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        log_pass "Landing page returns 200"
    else
        log_fail "Landing page failed with status: $status_code"
        return 1
    fi
}

# Test 3: Create Playlist
test_create_playlist() {
    log_test "Create Playlist"
    
    local playlist_name="e2e-test-$(date +%s)"
    local payload='{"songs": ["Test Song 1", "Test Song 2"], "genre": "test"}'
    
    local response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        -X POST "$API_ENDPOINT/$playlist_name" || echo -e "\n000")
    
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "201" ]; then
        log_pass "Playlist created successfully"
        echo "$playlist_name" > /tmp/e2e_playlist_name
    else
        log_fail "Create playlist failed with status: $status_code"
        echo "Response: $(echo "$response" | head -n -1)"
        return 1
    fi
}

# Test 4: Get Playlist
test_get_playlist() {
    log_test "Get Single Playlist"
    
    if [ ! -f /tmp/e2e_playlist_name ]; then
        log_fail "No test playlist name found"
        return 1
    fi
    
    local playlist_name=$(cat /tmp/e2e_playlist_name)
    local response=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT/$playlist_name" || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        local body=$(echo "$response" | head -n -1)
        if echo "$body" | grep -q '"songs"'; then
            log_pass "Playlist retrieved with correct structure"
        else
            log_fail "Playlist response missing expected fields"
            return 1
        fi
    else
        log_fail "Get playlist failed with status: $status_code"
        return 1
    fi
}

# Test 5: Update Playlist
test_update_playlist() {
    log_test "Update Playlist"
    
    if [ ! -f /tmp/e2e_playlist_name ]; then
        log_fail "No test playlist name found"
        return 1
    fi
    
    local playlist_name=$(cat /tmp/e2e_playlist_name)
    local payload='{"songs": ["Updated Song"], "genre": "updated"}'
    
    local response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        -X PUT "$API_ENDPOINT/$playlist_name" || echo -e "\n000")
    
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        log_pass "Playlist updated successfully"
    else
        log_fail "Update playlist failed with status: $status_code"
        return 1
    fi
}

# Test 6: List All Playlists
test_list_playlists() {
    log_test "List All Playlists"
    
    local response=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT" || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        local body=$(echo "$response" | head -n -1)
        if echo "$body" | grep -q '"playlists"'; then
            log_pass "Playlists list retrieved successfully"
        else
            log_fail "Playlists response missing expected structure"
            return 1
        fi
    else
        log_fail "List playlists failed with status: $status_code"
        return 1
    fi
}

# Test 7: Delete Playlist
test_delete_playlist() {
    log_test "Delete Playlist"
    
    if [ ! -f /tmp/e2e_playlist_name ]; then
        log_fail "No test playlist name found"
        return 1
    fi
    
    local playlist_name=$(cat /tmp/e2e_playlist_name)
    local response=$(curl -s -w "\n%{http_code}" \
        -X DELETE "$API_ENDPOINT/$playlist_name" || echo -e "\n000")
    
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        log_pass "Playlist deleted successfully"
    else
        log_fail "Delete playlist failed with status: $status_code"
        return 1
    fi
}

# Test 8: Verify Deletion (should return 404)
test_verify_deletion() {
    log_test "Verify Playlist Deletion"
    
    if [ ! -f /tmp/e2e_playlist_name ]; then
        log_fail "No test playlist name found"
        return 1
    fi
    
    local playlist_name=$(cat /tmp/e2e_playlist_name)
    local response=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT/$playlist_name" || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "404" ]; then
        log_pass "Playlist correctly returns 404 after deletion"
    else
        log_fail "Expected 404 for deleted playlist, got: $status_code"
        return 1
    fi
}

# Cleanup function
cleanup() {
    rm -f /tmp/e2e_playlist_name
}

# Main execution
main() {
    echo "Playlists API E2E Tests"
    echo "========================"
    echo ""
    
    # Wait for service to be ready
    if ! wait_for_service; then
        echo "Service readiness check failed!"
        exit 1
    fi
    
    echo ""
    
    # Run all tests (continue on failure to get full picture)
    test_health_check || true
    test_landing_page || true
    test_create_playlist || true
    test_get_playlist || true
    test_update_playlist || true
    test_list_playlists || true
    test_delete_playlist || true
    test_verify_deletion || true
    
    # Cleanup
    cleanup
    
    # Results summary
    echo ""
    echo "Test Results"
    echo "============"
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo "All tests passed"
        exit 0
    else
        echo "$FAILED_TESTS test(s) failed"
        exit 1
    fi
}

# Check dependencies
if ! command -v curl >/dev/null 2>&1; then
    echo "ERROR: curl is required but not installed"
    exit 1
fi

# Run main function
main "$@"