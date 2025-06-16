pipeline {
    agent { label 'linux-docker' }

    environment {
        DOCKER_IMAGE = 'redstonestart'
        DOCKER_TAG = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build --target=prod -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh """
                        docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} python manage.py test
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh "docker run ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed! Check the logs for details.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
    }
}