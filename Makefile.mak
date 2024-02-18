ifneq ("$(wildcard baseweb-demo)","")
	RUN_CMD=gunicorn -k eventlet -w 1 baseweb-demo:server
else
	INSTALL_CMD="git clone https://github.com/christophevg/baseweb-demo"
	ERROR_MSG="🛑‍ baseweb-demo is not present, so nothing to run..."
	RUN_CMD=@echo "$(RED)$(ERROR_MSG)$(NC)\nInstall using $(GREEN)$(INSTALL_CMD)$(NC)"
endif
