pipeline {
    agent { label 'linux-docker' }

    environment {
        DOCKER_IMAGE = 'redstonestart'
        DOCKER_TAG = 'latest'
        RESTART_POLICY = 'unless-stopped'
        TARGET_PORT = '8000'
        CONTAINER_NAME = 'redstonestart'
        DB_PORT = '3306'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Force Git Update') {
            steps {
                script {
                    sh """
                        git fetch --all
                        git reset --hard origin/master
                        git pull origin master
                    """
                }
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
                    withCredentials([
                        string(credentialsId: 'DB_REDSTONE_USER_MIGRATOR', variable: 'DB_USER'),
                        string(credentialsId: 'DB_REDSTONE_PASS_MIGRATOR', variable: 'DB_PASSWORD'),
                        string(credentialsId: 'DB_REDSTONE_HOST', variable: 'DB_HOST')
                    ]){
                        if (!DB_USER || !DB_PASSWORD || !DB_HOST) {
                            error "Missing credentials for database migration!"
                        }
                        withEnv(["DB_USER='${DB_USER}'", "DB_PASSWORD='${DB_PASSWORD}'", "DB_HOST='${DB_HOST}'", "DB_PORT='${DB_PORT}'"]) {
                            sh """
                                docker run --rm \
                                -e DB_USER=${DB_USER} \
                                -e DB_PASSWORD=${DB_PASSWORD} \
                                -e DB_HOST=${DB_HOST} \
                                -e DB_PORT=${DB_PORT} \
                                 ${DOCKER_IMAGE}:${DOCKER_TAG} \
                                 python manage.py migrate --noinput
                            """
                        }
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DB_REDSTONE_USER', variable: 'DB_USER'),
                        string(credentialsId: 'DB_REDSTONE_PASS', variable: 'DB_PASSWORD'),
                        string(credentialsId: 'DB_REDSTONE_HOST', variable: 'DB_HOST')
                    ]){
                        if (!DB_USER || !DB_PASSWORD || !DB_HOST) {
                            error "Missing credentials for running the application!"
                        }
                        sh """docker -p ${TARGET_PORT}:8000 --name "${CONTAINER_NAME}" -e DB_USER="${DB_USER}"\
                        -e DB_PASSWORD="${DB_PASSWORD}" -e DB_HOST="${DB_HOST}" -e DB_PORT="${DB_PORT}"\
                        --restart=${RESTART_POLICY} -d run ${DOCKER_IMAGE}:${DOCKER_TAG}"""
                    }
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