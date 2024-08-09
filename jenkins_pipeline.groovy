pipeline {
    agent any

    environment {
        // Set environment variables for Docker registry credentials
        PYTHON_PATH = 'C:\\Users\\panos\\AppData\\Local\\Programs\\Python\\Python311\\python.exe'
        MODELS_DOWNLOAD_SCRIPT = 'download_models.py'
        DOCKER_REGISTRY_CREDENTIALS = credentials('docker-registry-credentials')
        DOCKER_COMPOSE_FILE = 'app/docker-compose.yml'
    }

    stages {
        stage('Checkout') {
            steps {
                // Increase Git buffer size
                bat 'git config --global http.postBuffer 524288000'
                // Use credentials to clone the repository
                git branch: 'main', credentialsId: 'github-credentials', url: 'https://github.com/pkounelis/PersadoMLOps.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Install Python dependencies
                    bat "${env.PYTHON_PATH} -m pip install transformers torch --timeout=120"
                }
            }
        }

        stage('Download Models') {
            steps {
                script {
                    // Execute script to download models
                    bat "${env.PYTHON_PATH} ${env.MODELS_DOWNLOAD_SCRIPT}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker images using docker-compose
                    bat "docker-compose -f ${env.DOCKER_COMPOSE_FILE} build"
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    bat "docker login -u ${env.DOCKER_REGISTRY_CREDENTIALS_USR} -p ${env.DOCKER_REGISTRY_CREDENTIALS_PSW}"
                    bat "docker-compose -f ${env.DOCKER_COMPOSE_FILE} push"
                }
            }
        }

        stage('Clean Up') {
            steps {
                script {
                    // Clean up local Docker images to free space
                    bat "docker-compose -f ${env.DOCKER_COMPOSE_FILE} down --rmi all"
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
