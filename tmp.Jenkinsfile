
// // pipeline {
// //     agent any
    
// //     environment {
// //         // Application Configuration
// //         IMAGE_NAME = 'sara/playlists-app'
// //         ECR_URL = '793786247026.dkr.ecr.ap-south-1.amazonaws.com'
// //         ECR_REPO = "${ECR_URL}/${IMAGE_NAME}"
// //         AWS_DEFAULT_REGION = 'ap-south'
// //         // GitOps Configuration
// //         GITOPS_REPO = 'git@github.com:yourusername/gitops-config.git'
// //         GITOPS_BRANCH = 'main'
// //         HELM_VALUES_PATH = 'portfolio-app/values.yaml'
        
// //         // Dynamic Variables
// //         MAIN_TAG = ''
// //         DOCKER_IMAGE = "${ECR_REPO}:${TAG}"
// //         FAILURE_MSG = ''
// //     }
    
// //     triggers {
// //         githubPush()
// //     }
    
// //     stages {
// //         stage('Checkout & Setup') {
// //             steps {
// //                 checkout scm
// //                 script {
// //                     echo "Pipeline started for branch: ${env.BRANCH_NAME}"
// //                     echo "Build number: ${env.BUILD_NUMBER}"
// //                 }
// //             }
// //         }
        
// //         // stage('Code Quality & Security Analysis') {
// //         //     parallel {
// //         //         stage('Lint & Code Quality') {
// //         //             steps {
// //         //                 script {
// //         //                     sh '''
// //         //                         echo "Installing code quality tools..."
// //         //                         pip install flake8 pylint black isort
                                
// //         //                         echo "Running code formatting check..."
// //         //                         black --check app/ || true
// //         //                         isort --check-only app/ || true
                                
// //         //                         echo "Running flake8 linting..."
// //         //                         flake8 app/ --max-line-length=120 --ignore=E501,W503 --format=json --output-file=flake8-report.json || true
// //         //                         echo "Running pylint analysis..."
// //         //                         pylint app/ --output-format=json --reports=y > pylint-report.json || true
// //         //                     '''
// //         //                 }
// //         //             }
// //         //             post {
// //         //                 failure {
// //         //                     script {
// //         //                         FAILURE_MSG = "Code quality checks failed"
// //         //                     }
// //         //                 }
// //         //             }
// //         //         }
                
// //                 // stage('Security Scanning') {
// //                 //     steps {
// //                 //         script {
// //                 //             sh '''
// //                 //                 echo "Installing security scanning tools..."
// //                 //                 pip install safety bandit
                                
// //                 //                 echo "Scanning dependencies for vulnerabilities..."
// //                 //                 safety check --json --output safety-report.json || true
                                
// //                 //                 echo "Running bandit security scan..."
// //                 //                 bandit -r app/ -f json -o bandit-report.json || true
// //                 //             '''
// //                 //         }
// //                 //         archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
// //                 //     }
// //                 //     post {
// //                 //         failure {
// //                 //             script {
// //                 //                 FAILURE_MSG = "Security scanning failed"
// //                 //             }
// //                 //         }
// //                 //     }
// //                 // }
// //             }
// //         }
        
// //         stage('Unit Tests') {
// //             steps {
// //                 script {
// //                     sh '''
// //                         echo "Installing test dependencies..."
// //                         pip install -r requirements.txt
// //                         pip install pytest pytest-cov pytest-html pytest-json-report
                        
// //                         echo "Running unit tests with coverage..."
// //                         pytest app/tests/unit/ -v \
// //                             --cov=app \
// //                             --cov-report=html:coverage-html \
// //                             --cov-report=xml:coverage.xml \
// //                             --cov-report=term \
// //                             --html=unit-test-report.html \
// //                             --self-contained-html \
// //                             --json-report --json-report-file=unit-test-results.json
// //                     '''
// //                 }
// //             }
// //             post {
// //                 always {
// //                     publishHTML([
// //                         allowMissing: false,
// //                         alwaysLinkToLastBuild: true,
// //                         keepAll: true,
// //                         reportDir: 'coverage-html',
// //                         reportFiles: 'index.html',
// //                         reportName: 'Coverage Report'
// //                     ])
// //                     publishHTML([
// //                         allowMissing: false,
// //                         alwaysLinkToLastBuild: true,
// //                         keepAll: true,
// //                         reportDir: '.',
// //                         reportFiles: 'unit-test-report.html',
// //                         reportName: 'Unit Test Report'
// //                     ])
// //                 }
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "Unit tests failed"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('Build Docker Image') {
// //             steps {
// //                 script {
// //                     echo "Building Docker image..."
// //                     def image = docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
// //                     sh "docker images | grep ${IMAGE_NAME}"
// //                 }
// //             }
// //             post {
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "Docker image build failed"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('Integration & E2E Tests') {
// //             when {
// //                 anyOf {
// //                     branch 'main'
// //                     branch 'develop'
// //                     branch 'feature/*'
// //                 }
// //             }
// //             steps {
// //                 script {
// //                     sh '''
// //                         echo "Starting integration test environment..."
// //                         docker-compose up --build -d
                        
// //                         # Wait for services to be ready
// //                         echo "Waiting for services to be ready..."
// //                         sleep 45
                        
// //                         # Health check
// //                         echo "Performing health checks..."
// //                         curl -f http://localhost:5000/health || exit 1
                        
// //                         # Run integration tests
// //                         echo "Running integration tests..."
// //                         pip install requests pytest
// //                         pytest app/tests/integration/ -v \
// //                             --html=integration-test-report.html \
// //                             --self-contained-html || INTEGRATION_FAILED=true
                        
// //                         # Run E2E tests if script exists
// //                         if [ -f "./e2e.sh" ]; then
// //                             echo "Running E2E tests..."
// //                             chmod +x ./e2e.sh
// //                             ./e2e.sh localhost || E2E_FAILED=true
// //                         fi
                        
// //                         if [ "$INTEGRATION_FAILED" = "true" ] || [ "$E2E_FAILED" = "true" ]; then
// //                             exit 1
// //                         fi
// //                     '''
// //                 }
// //             }
// //             post {
// //                 always {
// //                     publishHTML([
// //                         allowMissing: true,
// //                         alwaysLinkToLastBuild: true,
// //                         keepAll: true,
// //                         reportDir: '.',
// //                         reportFiles: 'integration-test-report.html',
// //                         reportName: 'Integration Test Report'
// //                     ])
// //                     sh 'docker-compose down || true'
// //                 }
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "Integration/E2E tests failed"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('Docker Security Scan') {
// //             steps {
// //                 script {
// //                     sh '''
// //                         echo "Scanning Docker image for vulnerabilities..."
// //                         docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
// //                             aquasec/trivy:latest image \
// //                             --format json \
// //                             --output docker-security-report.json \
// //                             --severity HIGH,CRITICAL \
// //                             ${IMAGE_NAME}:${BUILD_NUMBER} || true
// //                     '''
// //                     archiveArtifacts artifacts: 'docker-security-report.json', allowEmptyArchive: true
// //                 }
// //             }
// //             post {
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "Docker security scan failed"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('Quality Gates') {
// //             steps {
// //                 script {
// //                     sh '''
// //                         echo "Checking quality gates..."
                        
// //                         # Check test coverage threshold (80%)
// //                         COVERAGE=$(python3 -c "
// // import xml.etree.ElementTree as ET
// // import sys
// // try:
// //     tree = ET.parse('coverage.xml')
// //     root = tree.getroot()
// //     coverage_percent = float(root.attrib['line-rate']) * 100
// //     print(f'{coverage_percent:.1f}')
// // except Exception as e:
// //     print('0')
// //     sys.stderr.write(f'Error reading coverage: {e}\\n')
// // ")
                        
// //                         echo "Test coverage: ${COVERAGE}%"
// //                         if (( $(echo "${COVERAGE} < 80" | bc -l) )); then
// //                             echo "ERROR: Test coverage ${COVERAGE}% is below required threshold of 80%"
// //                             exit 1
// //                         fi
                        
// //                         echo "Quality gates passed successfully ✅"
// //                     '''
// //                 }
// //             }
// //             post {
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "Quality gates failed - coverage below threshold"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('Set Version Tag') {
// //             when {
// //                 branch 'main'
// //             }
// //             steps {
// //                 script {
// //                     sshagent(['ssh-github']) {
// //                         sh "git fetch --tags"
// //                     }
                    
// //                     def tag = ''
// //                     def patch = 0
// //                     try {
// //                         tag = sh(script: "git describe --tags --abbrev=0", returnStdout: true).trim()
// //                         echo "Latest tag found: ${tag}"
// //                         def match = (tag =~ /(\d+)$/)
// //                         if (match) {
// //                             patch = (match[0][0] as int) + 1
// //                             MAIN_TAG = tag.replaceAll(/(\d+)$/, "${patch}")
// //                         } else {
// //                             MAIN_TAG = "${tag}.1"
// //                         }
// //                     } catch (Exception e) {
// //                         echo "No tags found, starting with v1.0.1"
// //                         MAIN_TAG = "v1.0.1"
// //                     }
                    
// //                     echo "New version tag: ${MAIN_TAG}"
// //                     DOCKER_IMAGE = "${ECR_REPO}:${MAIN_TAG}"
// //                 }
// //             }
// //             post {
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "Version tagging failed"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('Push Git Tag') {
// //             when {
// //                 branch 'main'
// //             }
// //             steps {
// //                 sshagent(['ssh-github']) {
// //                     sh """
// //                         git config user.email "jenkins@portfolio.com"
// //                         git config user.name "Jenkins CI"
// //                         git tag ${MAIN_TAG}
// //                         git push origin ${MAIN_TAG}
// //                     """
// //                 }
// //             }
// //             post {
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "Git tag push failed"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('Push to ECR') {
// //             when {
// //                 anyOf {
// //                     branch 'main'
// //                     branch 'develop'
// //                 }
// //             }
// //             steps {
// //                 script {
// //                     withAWS(credentials: 'aws-credentials', region: "${AWS_DEFAULT_REGION}") {
// //                         def imageTag = env.BRANCH_NAME == 'main' ? MAIN_TAG : "dev-${BUILD_NUMBER}"
// //                         DOCKER_IMAGE = "${ECR_REPO}:${imageTag}"
                        
// //                         sh """
// //                             echo "Logging into ECR..."
// //                             aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
// //                                 docker login --username AWS --password-stdin ${ECR_URL}
                            
// //                             echo "Tagging and pushing image: ${DOCKER_IMAGE}"
// //                             docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${DOCKER_IMAGE}
// //                             docker push ${DOCKER_IMAGE}
                            
// //                             # Also push latest tag for main branch
// //                             if [ "${env.BRANCH_NAME}" = "main" ]; then
// //                                 docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:latest
// //                                 docker push ${ECR_REPO}:latest
// //                             fi
                            
// //                             echo "Successfully pushed: ${DOCKER_IMAGE}"
// //                         """
// //                     }
// //                 }
// //             }
// //             post {
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "ECR push failed"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('GitOps Deployment') {
// //             when {
// //                 branch 'main'
// //             }
// //             steps {
// //                 script {
// //                     sshagent(['ssh-github']) {
// //                         sh '''
// //                             # Clean up any existing gitops directory
// //                             rm -rf gitops-config
                            
// //                             # Clone GitOps repository
// //                             echo "Cloning GitOps repository..."
// //                             git clone ${GITOPS_REPO} gitops-config
// //                         '''
                        
// //                         withCredentials([
// //                             string(credentialsId: 'git-username', variable: 'GIT_USERNAME'),
// //                             string(credentialsId: 'git-email', variable: 'GIT_EMAIL')
// //                         ]) {
// //                             dir('gitops-config') {
// //                                 sh """
// //                                     # Configure git
// //                                     git config user.email "${GIT_EMAIL}"
// //                                     git config user.name "${GIT_USERNAME}"
                                    
// //                                     # Update Helm values with new image tag
// //                                     echo "Updating image tag in ${HELM_VALUES_PATH}..."
// //                                     sed -i 's|tag:.*|tag: "${MAIN_TAG}"|g' ${HELM_VALUES_PATH}
// //                                     sed -i 's|app_image_version:.*|app_image_version: "${MAIN_TAG}"|g' ${HELM_VALUES_PATH}
                                    
// //                                     # Show changes
// //                                     echo "Changes made:"
// //                                     git diff
                                    
// //                                     # Commit and push
// //                                     git add ${HELM_VALUES_PATH}
// //                                     git commit -m "🚀 Deploy ${IMAGE_NAME} version ${MAIN_TAG}
                                    
// //                                     - Updated image tag to ${MAIN_TAG}
// //                                     - Build: ${BUILD_NUMBER}
// //                                     - Commit: ${GIT_COMMIT?.take(8)}"
                                    
// //                                     git push origin ${GITOPS_BRANCH}
                                    
// //                                     echo "✅ GitOps repository updated successfully!"
// //                                 """
// //                             }
// //                         }
// //                     }
// //                 }
// //             }
// //             post {
// //                 failure {
// //                     script {
// //                         FAILURE_MSG = "GitOps deployment update failed"
// //                     }
// //                 }
// //             }
// //         }
        
// //         stage('Create Deployment Artifact') {
// //             when {
// //                 branch 'main'
// //             }
// //             steps {
// //                 script {
// //                     sh """
// //                         # Create deployment summary
// //                         cat > deployment-info.json << EOF
// // {
// //     "application": "${IMAGE_NAME}",
// //     "version": "${MAIN_TAG}",
// //     "docker_image": "${DOCKER_IMAGE}",
// //     "build_number": "${BUILD_NUMBER}",
// //     "git_commit": "${GIT_COMMIT}",
// //     "branch": "${BRANCH_NAME}",
// //     "timestamp": "\$(date -u +%Y-%m-%dT%H:%M:%SZ)",
// //     "jenkins_build_url": "${BUILD_URL}"
// // }
// // EOF
                        
// //                         echo "Deployment completed successfully! 🎉"
// //                         echo "Version: ${MAIN_TAG}"
// //                         echo "Docker Image: ${DOCKER_IMAGE}"
// //                         cat deployment-info.json
// //                     """
// //                     archiveArtifacts artifacts: 'deployment-info.json'
// //                 }
// //             }
// //         }
// //     }
    
// //     post {
// //         always {
// //             script {
// //                 // Cleanup
// //                 sh '''
// //                     echo "Cleaning up..."
// //                     docker-compose down 2>/dev/null || true
// //                     docker images | grep ${IMAGE_NAME} | awk '{print $3}' | xargs -r docker rmi -f || true
// //                     docker system prune -f
// //                     rm -rf gitops-config
// //                 '''
                
// //                 // Archive all reports
// //                 archiveArtifacts artifacts: '**/*-report.json, **/*-report.html, coverage.xml, deployment-info.json', allowEmptyArchive: true
// //             }
            
// //             // Send notification email
// //             emailext(
// //                 subject: "🚀 ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${currentBuild.result}",
// //                 body: """
// //                 <h2>Pipeline Execution Summary</h2>
// //                 <p><strong>Status:</strong> ${currentBuild.result}</p>
// //                 <p><strong>Message:</strong> ${FAILURE_MSG}</p>
// //                 <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
// //                 <p><strong>Build:</strong> #${env.BUILD_NUMBER}</p>
// //                 ${env.BRANCH_NAME == 'main' && currentBuild.result == 'SUCCESS' ? 
// //                     "<p><strong>Deployed Version:</strong> ${MAIN_TAG}</p><p><strong>Docker Image:</strong> ${DOCKER_IMAGE}</p>" : 
// //                     ""}
// //                 <p><strong>Console Output:</strong> <a href="${env.BUILD_URL}/console">View Logs</a></p>
// //                 <p><strong>Test Reports:</strong> <a href="${env.BUILD_URL}">View Reports</a></p>
// //                 """,
// //                 to: "your-email@domain.com",
// //                 from: "jenkins@portfolio.com",
// //                 mimeType: 'text/html'
// //             )
// //         }
        
// //         success {
// //             script {
// //                 if (env.BRANCH_NAME == 'main') {
// //                     echo "🎉 Production deployment completed successfully!"
// //                     echo "Version ${MAIN_TAG} is now live!"
// //                 } else {
// //                     echo "✅ Pipeline completed successfully!"
// //                 }
// //             }
// //         }
        
// //         failure {
// //             echo "Check the logs above for detailed error information"
// //         }
        
// //         cleanup {
// //             deleteDir()
// //         }
// //     }
// // }



// pipeline {
//     agent any
    
//     environment {
//         // Application Configuration
//         IMAGE_NAME = 'sara/playlists-app'
//         ECR_URL = '793786247026.dkr.ecr.ap-south-1.amazonaws.com'
//         ECR_REPO = "${ECR_URL}/${IMAGE_NAME}"
//         AWS_DEFAULT_REGION = 'ap-south'
//         // GitOps Configuration
//         GITOPS_REPO = 'git@github.com:yourusername/gitops-config.git'
//         GITOPS_BRANCH = 'main'
//         HELM_VALUES_PATH = 'portfolio-app/values.yaml'
        
//         // Dynamic Variables
//         MAIN_TAG = ''
//         DOCKER_IMAGE = "${ECR_REPO}:${TAG}"
//         FAILURE_MSG = ''
//     }
    
//     triggers {
//         githubPush()
//     }
    
//     stages {
//         stage('Checkout & Setup') {
//             steps {
//                 checkout scm
//                 script {
//                     echo "Pipeline started for branch: ${env.BRANCH_NAME}"
//                     echo "Build number: ${env.BUILD_NUMBER}"
//                 }
//             }
//         }
        

//         stage('Unit Tests') {
//             steps {
//                 script {
//                     sh '''
//                         echo "Installing test dependencies..."
//                         pip install -r requirements.txt
//                         pip install pytest pytest-cov pytest-html pytest-json-report
                        
//                         echo "Running unit tests with coverage..."
//                         pytest app/tests/unit/ -v \
//                             --cov=app \
//                             --cov-report=html:coverage-html \
//                             --cov-report=xml:coverage.xml \
//                             --cov-report=term \
//                             --html=unit-test-report.html \
//                             --self-contained-html \
//                             --json-report --json-report-file=unit-test-results.json
//                     '''
//                 }
//             }
//             post {
//                 always {
//                     publishHTML([
//                         allowMissing: false,
//                         alwaysLinkToLastBuild: true,
//                         keepAll: true,
//                         reportDir: 'coverage-html',
//                         reportFiles: 'index.html',
//                         reportName: 'Coverage Report'
//                     ])
//                     publishHTML([
//                         allowMissing: false,
//                         alwaysLinkToLastBuild: true,
//                         keepAll: true,
//                         reportDir: '.',
//                         reportFiles: 'unit-test-report.html',
//                         reportName: 'Unit Test Report'
//                     ])
//                 }
//                 failure {
//                     script {
//                         FAILURE_MSG = "Unit tests failed"
//                     }
//                 }
//             }
//         }
        
//         stage('Build Docker Image') {
//             steps {
//                 script {
//                     echo "Building Docker image..."
//                     def image = docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
//                     sh "docker images | grep ${IMAGE_NAME}"
//                 }
//             }
//             post {
//                 failure {
//                     script {
//                         FAILURE_MSG = "Docker image build failed"
//                     }
//                 }
//             }
//         }
        
//         stage('Integration & E2E Tests') {
//             when {
//                 anyOf {
//                     branch 'main'
//                     branch 'develop'
//                     branch 'feature/*'
//                 }
//             }
//             steps {
//                 script {
//                     sh '''
//                         echo "Starting integration test environment..."
//                         docker-compose up --build -d
                        
//                         # Wait for services to be ready
//                         echo "Waiting for services to be ready..."
//                         sleep 45
                        
//                         # Health check
//                         echo "Performing health checks..."
//                         curl -f http://localhost:5000/health || exit 1
                        
//                         # Run integration tests
//                         echo "Running integration tests..."
//                         pip install requests pytest
//                         pytest app/tests/integration/ -v \
//                             --html=integration-test-report.html \
//                             --self-contained-html || INTEGRATION_FAILED=true
                        
//                         # Run E2E tests if script exists
//                         if [ -f "./e2e.sh" ]; then
//                             echo "Running E2E tests..."
//                             chmod +x ./e2e.sh
//                             ./e2e.sh localhost || E2E_FAILED=true
//                         fi
                        
//                         if [ "$INTEGRATION_FAILED" = "true" ] || [ "$E2E_FAILED" = "true" ]; then
//                             exit 1
//                         fi
//                     '''
//                 }
//             }
//             post {
//                 always {
//                     publishHTML([
//                         allowMissing: true,
//                         alwaysLinkToLastBuild: true,
//                         keepAll: true,
//                         reportDir: '.',
//                         reportFiles: 'integration-test-report.html',
//                         reportName: 'Integration Test Report'
//                     ])
//                     sh 'docker-compose down || true'
//                 }
//                 failure {
//                     script {
//                         FAILURE_MSG = "Integration/E2E tests failed"
//                     }
//                 }
//             }
//         }

        
        
//         stage('Set Version Tag') {
//             when {
//                 branch 'main'
//             }
//             steps {
//                 script {
//                     sshagent(['ssh-github']) {
//                         sh "git fetch --tags"
//                     }
                    
//                     def tag = ''
//                     def patch = 0
//                     try {
//                         tag = sh(script: "git describe --tags --abbrev=0", returnStdout: true).trim()
//                         echo "Latest tag found: ${tag}"
//                         def match = (tag =~ /(\d+)$/)
//                         if (match) {
//                             patch = (match[0][0] as int) + 1
//                             MAIN_TAG = tag.replaceAll(/(\d+)$/, "${patch}")
//                         } else {
//                             MAIN_TAG = "${tag}.1"
//                         }
//                     } catch (Exception e) {
//                         echo "No tags found, starting with v1.0.1"
//                         MAIN_TAG = "v1.0.1"
//                     }
                    
//                     echo "New version tag: ${MAIN_TAG}"
//                     DOCKER_IMAGE = "${ECR_REPO}:${MAIN_TAG}"
//                 }
//             }
//             post {
//                 failure {
//                     script {
//                         FAILURE_MSG = "Version tagging failed"
//                     }
//                 }
//             }
//         }
        
//         stage('Push Git Tag') {
//             when {
//                 branch 'main'
//             }
//             steps {
//                 sshagent(['ssh-github']) {
//                     sh """
//                         git config user.email "jenkins@portfolio.com"
//                         git config user.name "Jenkins CI"
//                         git tag ${MAIN_TAG}
//                         git push origin ${MAIN_TAG}
//                     """
//                 }
//             }
//             post {
//                 failure {
//                     script {
//                         FAILURE_MSG = "Git tag push failed"
//                     }
//                 }
//             }
//         }
        
//         stage('Push to ECR') {
//             when {
//                 anyOf {
//                     branch 'main'
//                     branch 'develop'
//                 }
//             }
//             steps {
//                 script {
//                     withAWS(credentials: 'aws-credentials', region: "${AWS_DEFAULT_REGION}") {
//                         def imageTag = env.BRANCH_NAME == 'main' ? MAIN_TAG : "dev-${BUILD_NUMBER}"
//                         DOCKER_IMAGE = "${ECR_REPO}:${imageTag}"
                        
//                         sh """
//                             echo "Logging into ECR..."
//                             aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
//                                 docker login --username AWS --password-stdin ${ECR_URL}
                            
//                             echo "Tagging and pushing image: ${DOCKER_IMAGE}"
//                             docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${DOCKER_IMAGE}
//                             docker push ${DOCKER_IMAGE}
                            
//                             # Also push latest tag for main branch
//                             if [ "${env.BRANCH_NAME}" = "main" ]; then
//                                 docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:latest
//                                 docker push ${ECR_REPO}:latest
//                             fi
                            
//                             echo "Successfully pushed: ${DOCKER_IMAGE}"
//                         """
//                     }
//                 }
//             }
//             post {
//                 failure {
//                     script {
//                         FAILURE_MSG = "ECR push failed"
//                     }
//                 }
//             }
//         }
        
//         stage('GitOps Deployment') {
//             when {
//                 branch 'main'
//             }
//             steps {
//                 script {
//                     sshagent(['ssh-github']) {
//                         sh '''
//                             # Clean up any existing gitops directory
//                             rm -rf gitops-config
                            
//                             # Clone GitOps repository
//                             echo "Cloning GitOps repository..."
//                             git clone ${GITOPS_REPO} gitops-config
//                         '''
                        
//                         withCredentials([
//                             string(credentialsId: 'git-username', variable: 'GIT_USERNAME'),
//                             string(credentialsId: 'git-email', variable: 'GIT_EMAIL')
//                         ]) {
//                             dir('gitops-config') {
//                                 sh """
//                                     # Configure git
//                                     git config user.email "${GIT_EMAIL}"
//                                     git config user.name "${GIT_USERNAME}"
                                    
//                                     # Update Helm values with new image tag
//                                     echo "Updating image tag in ${HELM_VALUES_PATH}..."
//                                     sed -i 's|tag:.*|tag: "${MAIN_TAG}"|g' ${HELM_VALUES_PATH}
//                                     sed -i 's|app_image_version:.*|app_image_version: "${MAIN_TAG}"|g' ${HELM_VALUES_PATH}
                                    
//                                     # Show changes
//                                     echo "Changes made:"
//                                     git diff
                                    
//                                     # Commit and push
//                                     git add ${HELM_VALUES_PATH}
//                                     git commit -m "🚀 Deploy ${IMAGE_NAME} version ${MAIN_TAG}
                                    
//                                     - Updated image tag to ${MAIN_TAG}
//                                     - Build: ${BUILD_NUMBER}
//                                     - Commit: ${GIT_COMMIT?.take(8)}"
                                    
//                                     git push origin ${GITOPS_BRANCH}
                                    
//                                     echo "✅ GitOps repository updated successfully!"
//                                 """
//                             }
//                         }
//                     }
//                 }
//             }
//             post {
//                 failure {
//                     script {
//                         FAILURE_MSG = "GitOps deployment update failed"
//                     }
//                 }
//             }
//         }
        
//         stage('Create Deployment Artifact') {
//             when {
//                 branch 'main'
//             }
//             steps {
//                 script {
//                     sh """
//                         # Create deployment summary
//                         cat > deployment-info.json << EOF
// {
//     "application": "${IMAGE_NAME}",
//     "version": "${MAIN_TAG}",
//     "docker_image": "${DOCKER_IMAGE}",
//     "build_number": "${BUILD_NUMBER}",
//     "git_commit": "${GIT_COMMIT}",
//     "branch": "${BRANCH_NAME}",
//     "timestamp": "\$(date -u +%Y-%m-%dT%H:%M:%SZ)",
//     "jenkins_build_url": "${BUILD_URL}"
// }
// EOF
                        
//                         echo "Deployment completed successfully! 🎉"
//                         echo "Version: ${MAIN_TAG}"
//                         echo "Docker Image: ${DOCKER_IMAGE}"
//                         cat deployment-info.json
//                     """
//                     archiveArtifacts artifacts: 'deployment-info.json'
//                 }
//             }
//         }
//     }
    
//     post {
//         always {
//             script {
//                 // Cleanup
//                 sh '''
//                     echo "Cleaning up..."
//                     docker-compose down 2>/dev/null || true
//                     docker images | grep ${IMAGE_NAME} | awk '{print $3}' | xargs -r docker rmi -f || true
//                     docker system prune -f
//                     rm -rf gitops-config
//                 '''
                
//                 // Archive all reports
//                 archiveArtifacts artifacts: '**/*-report.json, **/*-report.html, coverage.xml, deployment-info.json', allowEmptyArchive: true
//             }
            
//             // Send notification email
//             emailext(
//                 subject: "🚀 ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - ${currentBuild.result}",
//                 body: """
//                 <h2>Pipeline Execution Summary</h2>
//                 <p><strong>Status:</strong> ${currentBuild.result}</p>
//                 <p><strong>Message:</strong> ${FAILURE_MSG}</p>
//                 <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
//                 <p><strong>Build:</strong> #${env.BUILD_NUMBER}</p>
//                 ${env.BRANCH_NAME == 'main' && currentBuild.result == 'SUCCESS' ? 
//                     "<p><strong>Deployed Version:</strong> ${MAIN_TAG}</p><p><strong>Docker Image:</strong> ${DOCKER_IMAGE}</p>" : 
//                     ""}
//                 <p><strong>Console Output:</strong> <a href="${env.BUILD_URL}/console">View Logs</a></p>
//                 <p><strong>Test Reports:</strong> <a href="${env.BUILD_URL}">View Reports</a></p>
//                 """,
//                 to: "your-email@domain.com",
//                 from: "jenkins@portfolio.com",
//                 mimeType: 'text/html'
//             )
//         }
        
//         success {
//             script {
//                 if (env.BRANCH_NAME == 'main') {
//                     echo "🎉 Production deployment completed successfully!"
//                     echo "Version ${MAIN_TAG} is now live!"
//                 } else {
//                     echo "✅ Pipeline completed successfully!"
//                 }
//             }
//         }
        
//         failure {
//             echo "Check the logs above for detailed error information"
//         }
        
//         cleanup {
//             deleteDir()
//         }
//     }
// }



//strange way