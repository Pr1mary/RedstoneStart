pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'django-app'
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
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
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

        stage('Clean Up') {
            steps {
                script {
                    sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG}"
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