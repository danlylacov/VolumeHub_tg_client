docker-compose down -v

docker system prune -a

docker-compose build --no-cache --progress=plain making_photo_service

docker-compose up making_photo_service