#!/bin/bash

# E2E Tests for Playlists API - Clean & Minimal

set -e

# Configuration - Accept URL as parameter
BASE_URL=${1:-"http://localhost:5000"}
HEALTH_ENDPOINT="${BASE_URL}/health"
API_ENDPOINT="${BASE_URL}/playlists"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

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

# Wait for service (simplified)
wait_for_service() {
    log_info "Waiting for service at $BASE_URL"
    
    for i in {1..10}; do
        if curl -s -f "$HEALTH_ENDPOINT" >/dev/null 2>&1; then
            log_pass "Service ready after ${i} attempts"
            return 0
        fi
        echo "Attempt $i/10..."
        sleep 2
    done
    
    log_fail "Service not ready within timeout"
    return 1
}

# Test 1: Health Check
test_health() {
    log_test "Health Check"
    
    local response=$(curl -s -w "\n%{http_code}" "$HEALTH_ENDPOINT" 2>/dev/null || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        log_pass "Health endpoint responds with 200"
    else
        log_fail "Health check failed with status: $status_code"
        return 1
    fi
}

# Test 2: Landing Page
test_landing() {
    log_test "Landing Page"
    
    local response=$(curl -s -w "\n%{http_code}" "$BASE_URL/" 2>/dev/null || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ]; then
        log_pass "Landing page accessible"
    else
        log_fail "Landing page failed with status: $status_code"
        return 1
    fi
}

# Test 3: List Playlists
test_list_playlists() {
    log_test "List All Playlists"
    
    local response=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT" 2>/dev/null || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" = "200" ] && echo "$body" | grep -q '"playlists"'; then
        log_pass "Playlists list retrieved successfully"
    else
        log_fail "List playlists failed (status: $status_code)"
        return 1
    fi
}

# Test 4: Create & Delete Playlist
test_create_delete_playlist() {
    log_test "Create & Delete Playlist"
    
    local playlist_name="e2e-test-$(date +%s)"
    local payload='{"songs": ["Test Song"], "genre": "test"}'
    
    # Create playlist
    local create_response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        -X POST "$API_ENDPOINT/$playlist_name" 2>/dev/null || echo -e "\n000")
    
    local create_status=$(echo "$create_response" | tail -n1)
    
    if [ "$create_status" = "201" ]; then
        log_info "Playlist created successfully"
        
        # Get the created playlist
        local get_response=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT/$playlist_name" 2>/dev/null || echo -e "\n000")
        local get_status=$(echo "$get_response" | tail -n1)
        
        if [ "$get_status" = "200" ]; then
            log_info "Playlist retrieved successfully"
            
            # Delete the playlist
            local delete_response=$(curl -s -w "\n%{http_code}" -X DELETE "$API_ENDPOINT/$playlist_name" 2>/dev/null || echo -e "\n000")
            local delete_status=$(echo "$delete_response" | tail -n1)
            
            if [ "$delete_status" = "200" ]; then
                log_pass "Full CRUD cycle completed"
            else
                log_fail "Delete failed with status: $delete_status"
                return 1
            fi
        else
            log_fail "Get playlist failed with status: $get_status"
            # Cleanup attempt
            curl -s -X DELETE "$API_ENDPOINT/$playlist_name" >/dev/null 2>&1 || true
            return 1
        fi
    else
        log_fail "Create playlist failed with status: $create_status"
        return 1
    fi
}

# Test 5: Update Playlist
test_update_playlist() {
    log_test "Update Playlist"
    
    local playlist_name="e2e-update-$(date +%s)"
    local initial_payload='{"songs": ["Original Song"], "genre": "rock"}'
    local update_payload='{"songs": ["Updated Song"], "genre": "pop"}'
    
    # Create playlist
    local create_response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/json" \
        -d "$initial_payload" \
        -X POST "$API_ENDPOINT/$playlist_name" 2>/dev/null || echo -e "\n000")
    
    local create_status=$(echo "$create_response" | tail -n1)
    
    if [ "$create_status" = "201" ]; then
        # Update playlist
        local update_response=$(curl -s -w "\n%{http_code}" \
            -H "Content-Type: application/json" \
            -d "$update_payload" \
            -X PUT "$API_ENDPOINT/$playlist_name" 2>/dev/null || echo -e "\n000")
        
        local update_status=$(echo "$update_response" | tail -n1)
        
        if [ "$update_status" = "200" ]; then
            log_pass "Playlist updated successfully"
        else
            log_fail "Update failed with status: $update_status"
        fi
        
        # Cleanup
        curl -s -X DELETE "$API_ENDPOINT/$playlist_name" >/dev/null 2>&1 || true
    else
        log_fail "Could not create playlist for update test"
        return 1
    fi
}

# Test 6: Error Cases
test_error_cases() {
    log_test "Error Handling"
    
    # Test 404 - Get non-existent playlist
    local not_found_response=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT/non-existent-playlist" 2>/dev/null || echo -e "\n000")
    local not_found_status=$(echo "$not_found_response" | tail -n1)
    
    if [ "$not_found_status" = "404" ]; then
        log_info "404 for non-existent playlist - OK"
    else
        log_fail "Expected 404, got: $not_found_status"
        return 1
    fi
    
    # Test 400 - Invalid JSON
    local bad_json_response=$(curl -s -w "\n%{http_code}" \
        -H "Content-Type: application/json" \
        -d "invalid json" \
        -X POST "$API_ENDPOINT/test-bad-json" 2>/dev/null || echo -e "\n000")
    
    local bad_json_status=$(echo "$bad_json_response" | tail -n1)
    
    if [ "$bad_json_status" = "400" ]; then
        log_pass "Error handling works correctly"
    else
        log_fail "Expected 400 for bad JSON, got: $bad_json_status"
        return 1
    fi
}

# Main execution
main() {
    echo "Playlists API E2E Tests"
    echo "======================="
    echo "Testing: $BASE_URL"
    echo ""
    
    # Wait for service
    if ! wait_for_service; then
        echo "Service not available!"
        exit 1
    fi
    
    echo ""
    
    # Run tests
    test_health || true
    test_landing || true
    test_list_playlists || true
    test_create_delete_playlist || true
    test_update_playlist || true
    test_error_cases || true
    
    # Results
    echo ""
    echo "Test Results"
    echo "============"
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo "All tests passed!"
        exit 0
    else
        echo "Some tests failed!"
        exit 1
    fi
}

# Dependency check
if ! command -v curl >/dev/null 2>&1; then
    echo "ERROR: curl is required"
    exit 1
fi

# Run with URL parameter
main