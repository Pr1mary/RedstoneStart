pipeline {
    agent { label 'linux-docker' }

    environment {
        DOCKER_IMAGE = 'redstonestart'
        DOCKER_TAG = 'latest'
        RESTART_POLICY = 'unless-stopped'
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
        
        stage('DB Migration') {
            steps {
                script {
                    sh "docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} -e DB_USER=${DB_USER_MIGRATOR} -e DB_PASSWORD=${DB_PASSWORD_MIGRATOR} -e DB_HOST=${DB_HOST_MIGRATOR} python manage.py migrate --noinput"
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh "docker -p ${TARGET_PORT}:8000 --name ${CONTAINER_NAME} -e DB_USER=${DB_USER} -e DB_PASSWORD=${DB_PASSWORD} -e DB_HOST=${DB_HOST} -e DB_PORT=${DB_PORT} --restart=${RESTART_POLICY} -d run ${DOCKER_IMAGE}:${DOCKER_TAG}"
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