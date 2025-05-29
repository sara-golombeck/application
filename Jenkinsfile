pipeline {
    agent any
    
    environment {
        // Application Configuration
        IMAGE_NAME = 'sara/playlists-app'
        ECR_URL = '793786247026.dkr.ecr.ap-south-1.amazonaws.com'
        // ECR_REPO = "${ECR_URL}/${IMAGE_NAME}"
        ECR_REPO = "793786247026.dkr.ecr.ap-south-1.amazonaws.com/sara/playlists-app"
        AWS_REGION = 'ap-south-1'  
        // GitOps Configuration
        GITOPS_REPO = 'git@github.com:yourusername/gitops-config.git'
        GITOPS_BRANCH = 'main'
        HELM_VALUES_PATH = 'portfolio-app/values.yaml'
        // Dynamic Variables
        MAIN_TAG = ''
        FAILURE_MSG = ''
    }
    
    triggers {
        githubPush()
    }
    
    stages {
        stage('Checkout & Setup') {
            steps {
                checkout scm
                script {
                    echo "Pipeline started for branch: ${env.BRANCH_NAME}"
                    echo "Build number: ${env.BUILD_NUMBER}"
                }
            }
        }
        
// stage('Unit Tests') {
//     steps {
//         script {
//             sh 'docker build --target test --build-arg ENVIRONMENT=test -t myapp-test .'
//             sh 'docker run --rm myapp-test'

//         }
//     }
// }

        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image..."
                    def image = docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
                    sh "docker images | grep ${IMAGE_NAME}"
                }
            }
            post {
                success {
                    echo "Docker image built successfully"
                }
                failure {
                    script {
                        FAILURE_MSG = "Docker image build failed"
                        echo "Docker image build failed"
                    }
                }
            }
        }
        
        // stage('E2E Tests') {
        //     when {
        //         anyOf {
        //             branch 'main'
        //             branch 'develop'
        //             branch 'feature/*'
        //         }
        //     }
        //     steps {
        //         script {
        //             sh '''
        //                 ls -la app/nginx/
        //                 echo "Starting integration test environment..."
        //                 docker compose up --build -d 
        //                    chmod +x ./app/tests/e2e_tests/e2e_tests.sh
        //                    ./app/tests/e2e_tests/e2e_tests.sh localhost || E2E_FAILED=true
        //                    '''
        //         }
        //     }
        //     post {
        //         always {
        //             echo "Starting cleanup..."

        //             sh 'docker compose down || true'
        //         }
        //         success {
        //             echo "Integration/E2E tests passed successfully"
        //         }
        //         failure {
        //             script {
        //                 FAILURE_MSG = "Integration/E2E tests failed"
        //                 echo "Integration/E2E tests failed"
        //             }
        //         }
        //     }
        // }
        
// stage('Set And Push Image Tag') {
//     when { branch 'main' }
//     steps {
//         script {
//             def lastTag = sh(script: "git describe --tags --abbrev=0 2>/dev/null || echo '0.0.0'", returnStdout: true).trim()
//             def v = lastTag.tokenize('.')
//             MAIN_TAG = "${v[0]}.${v[1]}.${v[2].toInteger() + 1}"
            
//         sshagent (credentials: ['github'])
//         {
//             sh """
//                     git tag -a ${MAIN_TAG} -m "Release ${MAIN_TAG}"
//                     git push origin ${MAIN_TAG}
//             """
//         }
//         }
//     }
//  }

        
stage('Push to ECR') {
    when {
        anyOf {
            branch 'main'
        }
    }
    steps {
        script {
            def imageTag = env.BRANCH_NAME == 'main' ? MAIN_TAG : "dev-${BUILD_NUMBER}"
            
            sh """
                aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${ECR_URL}
                
                # Tag and push
                docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:${imageTag}
                docker push ${ECR_REPO}:${imageTag}
                
                # Push latest for main
                    docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:latest
                    docker push ${ECR_REPO}:latest
            """
        }
    }
}
        
        stage('GitOps Deployment') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sshagent(['ssh-github']) {
                        sh '''
                            # Clean up any existing gitops directory
                            rm -rf gitops-config
                            
                            # Clone GitOps repository
                            echo "Cloning GitOps repository..."
                            git clone ${GITOPS_REPO} gitops-config
                        '''
                        
                        withCredentials([
                            string(credentialsId: 'git-username', variable: 'GIT_USERNAME'),
                            string(credentialsId: 'git-email', variable: 'GIT_EMAIL')
                        ]) {
                            dir('gitops-config') {
                                sh """
                                    # Configure git
                                    git config user.email "${GIT_EMAIL}"
                                    git config user.name "${GIT_USERNAME}"
                                    
                                    # Update Helm values with new image tag
                                    echo "Updating image tag in ${HELM_VALUES_PATH}..."
                                    sed -i 's|tag:.*|tag: "${MAIN_TAG}"|g' ${HELM_VALUES_PATH}
                                    sed -i 's|app_image_version:.*|app_image_version: "${MAIN_TAG}"|g' ${HELM_VALUES_PATH}
                                    
                                    # Show changes
                                    echo "Changes made:"
                                    git diff
                                    
                                    # Commit and push
                                    git add ${HELM_VALUES_PATH}
                                    git commit -m "Deploy ${IMAGE_NAME} version ${MAIN_TAG}
                                    
                                    - Updated image tag to ${MAIN_TAG}
                                    - Build: ${BUILD_NUMBER}
                                    - Commit: ${GIT_COMMIT?.take(8)}"
                                    
                                    git push origin ${GITOPS_BRANCH}
                                    
                                    echo "GitOps repository updated successfully!"
                                """
                            }
                        }
                    }
                }
            }
            post {
                success {
                    echo "GitOps deployment updated successfully"
                }
                failure {
                    script {
                        FAILURE_MSG = "GitOps deployment update failed"
                        echo "GitOps deployment update failed"
                    }
                }
            }
        }
        
        stage('Create Deployment Artifact') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh """
                        # Create deployment summary
                        cat > deployment-info.json << EOF
{
    "application": "${IMAGE_NAME}",
    "version": "${MAIN_TAG}",
    "docker_image": "${ECR_REPO}:${MAIN_TAG}",
    "build_number": "${BUILD_NUMBER}",
    "git_commit": "${GIT_COMMIT}",
    "branch": "${BRANCH_NAME}",
    "timestamp": "\$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "jenkins_build_url": "${BUILD_URL}"
}
EOF
                        
                        echo "Deployment completed successfully!"
                        echo "Version: ${MAIN_TAG}"
                        echo "Docker Image: ${ECR_REPO}:${MAIN_TAG}"
                        cat deployment-info.json
                    """
                    archiveArtifacts artifacts: 'deployment-info.json'
                }
            }
            post {
                success {
                    echo "Deployment artifact created successfully"
                }
            }
        }
    }
    
    post {
        always {
            script {
                // Cleanup
                sh '''
                    echo "Cleaning up..."
                    # docker compose down 2>/dev/null || true
                    docker images | grep ${IMAGE_NAME} | awk '{print $3}' | xargs -r docker rmi -f || true
                    docker system prune -f
                    rm -rf gitops-config
                '''
                
                // Archive important files
                archiveArtifacts artifacts: 'deployment-info.json', allowEmptyArchive: true
            }
        }
        
        success {
            script {
                if (env.BRANCH_NAME == 'main') {
                    echo "Production deployment completed successfully!"
                    echo "Version ${MAIN_TAG} is now live!"
                } else {
                    echo "Pipeline completed successfully!"
                }
            }
        }
        
        failure {
            echo "Pipeline failed: ${FAILURE_MSG}"
            echo "Check the logs above for detailed error information"
        }
        
        // cleanup {
        //     deleteDir()
        // }
    }
}