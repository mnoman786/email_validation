#!/usr/bin/env bash
# Quick helper for managing EmailGuard services on Ubuntu.
# Usage:  bash manage_service.sh [command]

BACKEND="emailguard-backend"
FRONTEND="emailguard-frontend"

case "${1:-help}" in
  start)
    sudo systemctl start  $BACKEND $FRONTEND
    echo "Services started."
    ;;
  stop)
    sudo systemctl stop   $BACKEND $FRONTEND
    echo "Services stopped."
    ;;
  restart)
    sudo systemctl restart $BACKEND $FRONTEND
    echo "Services restarted."
    ;;
  status)
    sudo systemctl status  $BACKEND --no-pager -l
    echo "---"
    sudo systemctl status  $FRONTEND --no-pager -l
    ;;
  logs-backend)
    sudo journalctl -u $BACKEND -f --no-pager
    ;;
  logs-frontend)
    sudo journalctl -u $FRONTEND -f --no-pager
    ;;
  logs)
    sudo journalctl -u $BACKEND -u $FRONTEND -f --no-pager
    ;;
  update)
    sudo bash "$(dirname "$0")/setup_ubuntu.sh" --update
    ;;
  *)
    echo "EmailGuard Service Manager"
    echo ""
    echo "Usage: bash manage_service.sh <command>"
    echo ""
    echo "Commands:"
    echo "  start           Start both services"
    echo "  stop            Stop both services"
    echo "  restart         Restart both services"
    echo "  status          Show service status"
    echo "  logs            Stream logs from both services"
    echo "  logs-backend    Stream backend logs only"
    echo "  logs-frontend   Stream frontend logs only"
    echo "  update          Pull latest & rebuild (runs setup_ubuntu.sh --update)"
    ;;
esac
