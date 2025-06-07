// pipeline {
//     agent any
    
//     environment {
//         // Application Configuration
//         IMAGE_NAME = 'sara/playlists-app'
//         ECR_URL = '793786247026.dkr.ecr.ap-south-1.amazonaws.com'
//         ECR_REPO = "793786247026.dkr.ecr.ap-south-1.amazonaws.com/sara/playlists-app"
//         AWS_REGION = 'ap-south-1'  
//         GITOPS_REPO = 'git@github.com:sara-golombeck/gitops.git'
//         GITOPS_BRANCH = 'main'
//         HELM_VALUES_PATH = 'charts/playlist-app/values.yaml'
//         MAIN_TAG = ''
//     }
    
//     triggers {
//         githubPush()
//     }
    
//     stages {
//         stage('Checkout') {
//             steps {
//                 checkout scm
//             }
//         }
        
//         stage('Unit Tests') {
//             steps {
//                 script {
//                     sh 'docker build --target test --build-arg ENVIRONMENT=test -t myapp-test .'
//                     sh 'docker run --rm myapp-test'
//                 }
//             }
//             post {
//                 always {
//                     sh 'docker rmi myapp-test || true'
//                 }
//                 failure {
//                     script {
//                         echo "Unit tests failed"
//                     }
//                 }
//             }
//         }
       
//         stage('Package') {
//             steps {
//                 script {
//                     echo "Building Docker image."
//                     def image = docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
//                 }
//             }
//             post {
//                 success {
//                     echo "Docker image built successfully"
//                 }
//                 failure {
//                     script {
//                         echo "Docker image build failed"
//                     }
//                 }
//             }
//         }
        
//         // stage('E2E Tests') {
//         //     when {
//         //         anyOf {
//         //             branch 'main'
//         //             branch 'feature/*'
//         //         }
//         //     }
//         //     steps {
//         //         script {
//         //             sh '''
//         //                 docker compose up --build -d 
//         //                 chmod +x ./app/tests/e2e_tests/e2e_tests.sh
//         //                 ./app/tests/e2e_tests/e2e_tests.sh localhost
//         //                 '''
//         //         }
//         //     }
//         //     post {
//         //         always {
//         //             echo "Cleaning up test environment."
//         //             sh 'docker compose down || true'
//         //         }
//         //         success {
//         //             echo "E2E tests passed successfully"
//         //         }
//         //         failure {
//         //             script {
//         //                 echo "E2E tests failed"
//         //             }
//         //         }
//         //     }
//         // }

//         stage('Create Version Tag') {
//             when { 
//                 branch 'main' 
//             }
//             steps {
//                 script {
//                     echo "Creating version tag..."
                    
//                     def lastTag = sh(script: "git describe --tags --abbrev=0 2>/dev/null || echo '0.0.0'", returnStdout: true).trim()
//                     def v = lastTag.tokenize('.')
//                     env.MAIN_TAG = "${v[0]}.${v[1]}.${v[2].toInteger() + 1}"
                    
//                     def tagExists = sh(script: "git tag -l ${env.MAIN_TAG}", returnStdout: true).trim()
//                     if (tagExists) {
//                         error("Tag ${env.MAIN_TAG} already exists!")
//                     }
                    
//                     echo "Version tag ${env.MAIN_TAG} prepared successfully"
//                 }
//             }
//         }

//         stage('Push to ECR') {
//             when { 
//                 allOf {
//                     branch 'main'
//                     // expression { env.MAIN_TAG != '' }
//                 }
//             }
//             steps {

//                 script {
//                             if (!env.MAIN_TAG || env.MAIN_TAG == '') {  // בדיקה בזמן רצה
//             return
//         }


//                     sh """
//                         aws ecr get-login-password --region ${AWS_REGION} | \
//                             docker login --username AWS --password-stdin ${ECR_URL}
                        
//                         docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:${env.MAIN_TAG}
//                         docker push ${ECR_REPO}:${envMAIN_TAG}
                        
//                         docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:latest
//                         docker push ${ECR_REPO}:latest
//                     """
//                 }
//             }
//         }

//         stage('Push Tag') {
//             when { 
//                 allOf {
//                     branch 'main'
//                     // expression { env.MAIN_TAG != '' }
//                 }
//             }
//             steps {
//                 script {
//                     echo "Pushing tag to repository..."
                    
//                     sshagent(credentials: ['github']) {
//                         withCredentials([
//                             string(credentialsId: 'git-username', variable: 'GIT_USERNAME'),
//                             string(credentialsId: 'git-email', variable: 'GIT_EMAIL')
//                         ]) {
//                             sh """
//                                 git config user.email "${GIT_EMAIL}"
//                                 git config user.name "${GIT_USERNAME}"
                                
//                                 git tag -a ${env.MAIN_TAG} -m "Release ${env.MAIN_TAG}"
//                                 git push origin ${env.MAIN_TAG}
//                             """
//                         }
//                     }
                    
//                     echo "Tag ${env.MAIN_TAG} pushed successfully"
//                 }
//             }
//         }

//         stage('GitOps') {
//             when { 
//                 branch 'main' 
//             }
//             steps {
//                 script {
//                     sshagent(['github']) {
//                         sh '''
//                             rm -rf gitops-config
//                             echo "Cloning GitOps repository..."
//                             git clone ${GITOPS_REPO} gitops-config
//                         '''
                        
//                         withCredentials([
//                             string(credentialsId: 'git-username', variable: 'GIT_USERNAME'),
//                             string(credentialsId: 'git-email', variable: 'GIT_EMAIL')
//                         ]) {
//                             dir('gitops-config') {
//                                 sh """
//                                     git config user.email "${GIT_EMAIL}"
//                                     git config user.name "${GIT_USERNAME}"

//                                     sed -i 's|tag: ".*"|tag: "${env.MAIN_TAG}"|g' ${HELM_VALUES_PATH}
                                    
//                                     if git diff --quiet ${HELM_VALUES_PATH}; then
//                                         echo "No changes to deploy - version ${env.MAIN_TAG} already deployed"
//                                     else
//                                         git add ${HELM_VALUES_PATH}
//                                         git commit -m "Deploy ${IMAGE_NAME} v${env.MAIN_TAG} - Build ${BUILD_NUMBER}"
//                                         git push origin ${GITOPS_BRANCH}
//                                         echo "GitOps updated: ${env.MAIN_TAG}"
//                                     fi
//                                 """
//                             }
//                         }
//                     }
//                 }
//             }
//             post {
//                 success {
//                     echo "GitOps deployment updated successfully"
//                 }
//                 failure {
//                     echo "GitOps deployment update failed"
//                 }
//             }
//         }
//     }

//     post {
//         always {
//             script {
//                 def status = currentBuild.result ?: 'SUCCESS'
//                 emailext (
//                     subject: "${IMAGE_NAME} Pipeline ${status}",
//                     body: "Build #${BUILD_NUMBER} | Branch: ${BRANCH_NAME} | Version: ${env.MAIN_TAG ?: 'N/A'}",
//                     to: 'sara.beck.dev@gmail.com'
//                 )
//             }
            
//             sh '''
//                 docker compose down -v || true
//                 rm -rf gitops-config || true
//             '''
//         }
        
//         success {
//             echo "Pipeline completed successfully!"
//         }
        
//         failure {
//             echo "Pipeline failed"
//         }
        
//         cleanup {
//             deleteDir()
//         }
//     }
// }


pipeline {
    agent any
    
    environment {
        // Application Configuration
        IMAGE_NAME = 'sara/playlists-app'
        ECR_URL = '793786247026.dkr.ecr.ap-south-1.amazonaws.com'
        ECR_REPO = "793786247026.dkr.ecr.ap-south-1.amazonaws.com/sara/playlists-app"
        AWS_REGION = 'ap-south-1'  
        GITOPS_REPO = 'git@github.com:sara-golombeck/gitops.git'
        GITOPS_BRANCH = 'main'
        HELM_VALUES_PATH = 'charts/playlist-app/values.yaml'
        MAIN_TAG = ''
    }
    
    triggers {
        githubPush()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    sh 'docker build --target test --build-arg ENVIRONMENT=test -t myapp-test .'
                    sh 'docker run --rm myapp-test'
                }
            }
            post {
                always {
                    sh 'docker rmi myapp-test || true'
                }
                failure {
                    script {
                        echo "Unit tests failed"
                    }
                }
            }
        }
       
        stage('Package') {
            steps {
                script {
                    echo "Building Docker image."
                    def image = docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
            post {
                success {
                    echo "Docker image built successfully"
                }
                failure {
                    script {
                        echo "Docker image build failed"
                    }
                }
            }
        }
        
        // stage('E2E Tests') {
        //     when {
        //         anyOf {
        //             branch 'main'
        //             branch 'feature/*'
        //         }
        //     }
        //     steps {
        //         script {
        //             sh '''
        //                 docker compose up --build -d 
        //                 chmod +x ./app/tests/e2e_tests/e2e_tests.sh
        //                 ./app/tests/e2e_tests/e2e_tests.sh localhost
        //                 '''
        //         }
        //     }
        //     post {
        //         always {
        //             echo "Cleaning up test environment."
        //             sh 'docker compose down || true'
        //         }
        //         success {
        //             echo "E2E tests passed successfully"
        //         }
        //         failure {
        //             script {
        //                 echo "E2E tests failed"
        //             }
        //         }
        //     }
        // }

        stage('Create Version Tag') {
            when { 
                branch 'main' 
            }
            steps {
                script {
                    echo "Creating version tag..."
                    
                    try {
                        def lastTag = sh(script: "git describe --tags --abbrev=0 2>/dev/null || echo '0.0.0'", returnStdout: true).trim()
                        def v = lastTag.tokenize('.')
                        env.MAIN_TAG = "${v[0]}.${v[1]}.${v[2].toInteger() + 1}"
                        
                        if (!env.MAIN_TAG || env.MAIN_TAG == 'null') {
                            env.MAIN_TAG = "0.0.1"
                        }
                        
                        def tagExists = sh(script: "git tag -l ${env.MAIN_TAG}", returnStdout: true).trim()
                        if (tagExists) {
                            error("Tag ${env.MAIN_TAG} already exists!")
                        }
                        
                        echo "Version tag ${env.MAIN_TAG} prepared successfully"
                        
                    } catch (Exception e) {
                        echo "Error in version tagging: ${e.getMessage()}"
                        env.MAIN_TAG = "0.0.1"
                        echo "Using fallback version: ${env.MAIN_TAG}"
                    }
                }
            }
        }

        stage('Push to ECR') {
            when { 
                allOf {
                    branch 'main'
                    // expression { env.MAIN_TAG != '' }
                }
            }
            steps {
                script {
                    if (!env.MAIN_TAG || env.MAIN_TAG == '') {
                        echo "WARNING: MAIN_TAG not set, skipping ECR push"
                        return
                    }
                    
                    echo "Pushing ${env.MAIN_TAG} to ECR..."
                    
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${ECR_URL}
                        
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:${env.MAIN_TAG}
                        docker push ${ECR_REPO}:${env.MAIN_TAG}
                        
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:latest
                        docker push ${ECR_REPO}:latest
                    """
                    
                    echo "Successfully pushed ${env.MAIN_TAG} to ECR"
                }
            }
        }

        stage('Push Tag') {
            when { 
                allOf {
                    branch 'main'
                    // expression { env.MAIN_TAG != '' }
                }
            }
            steps {
                script {
                    if (!env.MAIN_TAG || env.MAIN_TAG == '') {
                        echo "WARNING: MAIN_TAG not set, skipping git tag"
                        return
                    }
                    
                    echo "Pushing tag ${env.MAIN_TAG} to repository..."
                    
                    sshagent(credentials: ['github']) {
                        withCredentials([
                            string(credentialsId: 'git-username', variable: 'GIT_USERNAME'),
                            string(credentialsId: 'git-email', variable: 'GIT_EMAIL')
                        ]) {
                            sh """
                                git config user.email "${GIT_EMAIL}"
                                git config user.name "${GIT_USERNAME}"
                                
                                git tag -a ${env.MAIN_TAG} -m "Release ${env.MAIN_TAG}"
                                git push origin ${env.MAIN_TAG}
                            """
                        }
                    }
                    
                    echo "Tag ${env.MAIN_TAG} pushed successfully"
                }
            }
        }

        stage('GitOps') {
            when { 
                branch 'main' 
            }
            steps {
                script {
                    if (!env.MAIN_TAG || env.MAIN_TAG == '') {
                        echo "WARNING: MAIN_TAG not set, skipping GitOps update"
                        return
                    }
                    
                    sshagent(['github']) {
                        sh '''
                            rm -rf gitops-config
                            echo "Cloning GitOps repository..."
                            git clone ${GITOPS_REPO} gitops-config
                        '''
                        
                        withCredentials([
                            string(credentialsId: 'git-username', variable: 'GIT_USERNAME'),
                            string(credentialsId: 'git-email', variable: 'GIT_EMAIL')
                        ]) {
                            dir('gitops-config') {
                                sh """
                                    git config user.email "${GIT_EMAIL}"
                                    git config user.name "${GIT_USERNAME}"

                                    sed -i 's|tag: ".*"|tag: "${env.MAIN_TAG}"|g' ${HELM_VALUES_PATH}
                                    
                                    if git diff --quiet ${HELM_VALUES_PATH}; then
                                        echo "No changes to deploy - version ${env.MAIN_TAG} already deployed"
                                    else
                                        git add ${HELM_VALUES_PATH}
                                        git commit -m "Deploy ${IMAGE_NAME} v${env.MAIN_TAG} - Build ${BUILD_NUMBER}"
                                        git push origin ${GITOPS_BRANCH}
                                        echo "GitOps updated: ${env.MAIN_TAG}"
                                    fi
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
                    echo "GitOps deployment update failed"
                }
            }
        }
    }

    post {
        always {
            script {
                def status = currentBuild.result ?: 'SUCCESS'
                emailext (
                    subject: "${IMAGE_NAME} Pipeline ${status}",
                    body: "Build #${BUILD_NUMBER} | Branch: ${BRANCH_NAME} | Version: ${env.MAIN_TAG ?: 'N/A'}",
                    to: 'sara.beck.dev@gmail.com'
                )
            }
            
            sh '''
                docker compose down -v || true
                rm -rf gitops-config || true
            '''
        }
        
        success {
            echo "Pipeline completed successfully!"
        }
        
        failure {
            echo "Pipeline failed"
        }
        
        cleanup {
            deleteDir()
        }
    }
}