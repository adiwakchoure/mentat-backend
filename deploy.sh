# curl -L https://fly.io/install.sh | sh
curl -L https://fly.io/install.sh
export FLYCTL_INSTALL="/home/codespace/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
# fly auth login