def stop_success
def rename_success
def remove_success
def rollback_container

pipeline {
    agent { label 'linux-docker' }

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
                    sh "docker build --target=${APP_MODE} -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh """
                        docker run --rm -e CSRF_TRUSTED_ORIGINS_LIST=${CSRF_TRUSTED_ORIGINS_LIST} ${DOCKER_IMAGE}:${DOCKER_TAG} python manage.py test
                    """
                }
            }
        }
        
        stage('DB Migration') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DB_REDSTONE_USER_MIGRATOR', variable: 'DB_USER'),
                        string(credentialsId: 'DB_REDSTONE_PASS_MIGRATOR', variable: 'DB_PASSWORD')
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
                                -e CSRF_TRUSTED_ORIGINS_LIST=${CSRF_TRUSTED_ORIGINS_LIST} \
                                ${DOCKER_IMAGE}:${DOCKER_TAG} \
                                python manage.py migrate --noinput
                            """
                        }
                    }
                }
            }
        }

        stage("Stop Old Container"){
            steps {
                script {
                    // stop container process
                    stop_success = sh (
                        script: "docker stop ${CONTAINER_NAME}",
                        returnStatus: true 
                    )

                    echo "Stop status (${stop_success})"
                }
            }
        }

        stage("Backup Old Container"){
            steps {
                script {
                    // rename container process
                    rename_success = sh (
                        script: "docker rename ${CONTAINER_NAME} ${CONTAINER_NAME}-OLD",
                        returnStatus: true 
                    )

                    echo "Backup status (${rename_success})"
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DB_REDSTONE_USER', variable: 'DB_USER'),
                        string(credentialsId: 'DB_REDSTONE_PASS', variable: 'DB_PASSWORD'),
                        string(credentialsId: 'DJANGO_SECRET', variable: 'DJANGO_SECRET')
                    ]){
                        if (!DB_USER || !DB_PASSWORD || !CSRF_TRUSTED_ORIGINS_LIST || !DJANGO_SECRET) {
                            error "Missing credentials for running the application!"
                        }
                        
                        withEnv(["DB_USER='${DB_USER}'", "DB_PASSWORD='${DB_PASSWORD}'", "DJANGO_SECRET='${DJANGO_SECRET}'", "DB_HOST='${DB_HOST}'", "DB_PORT='${DB_PORT}'"]) {
                            sh """
                                docker run -p ${TARGET_PORT}:8000 \
                                --name "${CONTAINER_NAME}" -e DB_USER=${DB_USER} -e APP_URL=${APP_URL} \
                                -e CSRF_TRUSTED_ORIGINS_LIST=${CSRF_TRUSTED_ORIGINS_LIST} -e ALLOWED_HOST_LIST=${ALLOWED_HOST_LIST} \
                                -e DB_PASSWORD=${DB_PASSWORD} -e DB_HOST=${DB_HOST} \
                                -e DJANGO_SECRET=${DJANGO_SECRET} -e DB_PORT=${DB_PORT} \
                                --restart=${RESTART_POLICY} -d ${DOCKER_IMAGE}:${DOCKER_TAG}
                            """
                        }

                        rollback_container = false
                        echo "Container named ${CONTAINER_NAME} is running!"
                    }
                }
            }
            post {
                failure {
                    rollback_container = true
                }
                
            }
        }

        stage("Rollback Old Container"){
            when {
                expression {
                    rename_success == 0 && rollback_container
                }
            }
            steps {
                script {
                    // delete container then put it on grep so that it won't return error if container not found
                    rename_status = sh (
                        script: "docker rename ${CONTAINER_NAME}-OLD ${CONTAINER_NAME}",
                        returnStatus: true 
                    )

                    start_status = sh (
                        script: "docker start ${CONTAINER_NAME}",
                        returnStatus: true 
                    )

                    echo "Rollback status (${rename_status} - ${start_status})"
                }
            }
        }

        stage("Remove Old Container"){
            when {
                expression {
                    rename_success == 0 && !rollback_container
                }
            }
            steps {
                script {
                    // delete container then put it on grep so that it won't return error if container not found
                    remove_success = sh (
                        script: "docker rm ${CONTAINER_NAME}-OLD",
                        returnStatus: true 
                    )

                    echo "Remove return status (${remove_success})"
                }
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed! Affected container will be rolled back, check the logs for details.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
    }
}