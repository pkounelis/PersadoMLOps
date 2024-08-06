pipeline {
    agent any

    environment {
        // Set environment variables for Docker registry credentials
        DOCKER_REGISTRY_CREDENTIALS = credentials('docker-registry-credentials')
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout code from the repository
                git 'https://github.com/pkounelis/PersadoMLOps.git/'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker images using docker-compose
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} build'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Push Docker images to the registry
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-registry-credentials') {
                        sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} push'
                    }
                }
            }
        }

        stage('Clean Up') {
            steps {
                script {
                    // Clean up local Docker images to free space
                    sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} down --rmi all'
                }
            }
        }
    }

    post {
        always {
            // Clean workspace after the build
            cleanWs()
        }
        success {
            echo 'Build and push successful!'
        }
        failure {
            echo 'Build or push failed.'
        }
    }
}
