#!/bin/bash
# ============================================================================
# ProInvestiX Enterprise - Deployment Script
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check requirements
check_requirements() {
    log_info "Checking requirements..."
    
    command -v docker >/dev/null 2>&1 || { log_error "Docker is required but not installed."; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { log_error "Docker Compose is required but not installed."; exit 1; }
    
    log_success "All requirements satisfied"
}

# Build images
build_images() {
    log_info "Building Docker images..."
    
    docker-compose -f docker/docker-compose.yml build --no-cache
    
    log_success "Docker images built successfully"
}

# Start services
start_services() {
    log_info "Starting services..."
    
    docker-compose -f docker/docker-compose.yml up -d
    
    log_success "Services started successfully"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    
    docker-compose -f docker/docker-compose.yml down
    
    log_success "Services stopped successfully"
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."
    
    docker-compose -f docker/docker-compose.yml exec api alembic upgrade head
    
    log_success "Migrations completed successfully"
}

# Show logs
show_logs() {
    log_info "Showing logs..."
    
    docker-compose -f docker/docker-compose.yml logs -f
}

# Health check
health_check() {
    log_info "Running health check..."
    
    sleep 10
    
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        log_success "API is healthy"
    else
        log_error "API health check failed"
        exit 1
    fi
    
    if curl -s http://localhost:3000 | grep -q "ProInvestiX"; then
        log_success "Frontend is healthy"
    else
        log_warning "Frontend health check failed (may still be starting)"
    fi
}

# Full deployment
deploy() {
    log_info "Starting full deployment..."
    
    check_requirements
    build_images
    start_services
    run_migrations
    health_check
    
    log_success "Deployment completed successfully!"
    echo ""
    echo "Access the application:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API:      http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
}

# Print usage
usage() {
    echo "Usage: $0 {deploy|build|start|stop|logs|migrate|health}"
    echo ""
    echo "Commands:"
    echo "  deploy   - Full deployment (build, start, migrate)"
    echo "  build    - Build Docker images"
    echo "  start    - Start services"
    echo "  stop     - Stop services"
    echo "  logs     - Show service logs"
    echo "  migrate  - Run database migrations"
    echo "  health   - Run health check"
}

# Main
case "$1" in
    deploy)
        deploy
        ;;
    build)
        build_images
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    logs)
        show_logs
        ;;
    migrate)
        run_migrations
        ;;
    health)
        health_check
        ;;
    *)
        usage
        exit 1
        ;;
esac
