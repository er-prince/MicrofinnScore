echo '1. Setting up ubuntu locale...'
export LC_ALL="en_US.UTF-8"
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
sudo dpkg-reconfigure locales
echo '2. Cloning github...'
git clone http://github.com/piy0999/CreditSense.git
cd ~/CreditSense
git config credential.helper store
cd ~
echo '3. Installing python3 pip...'
sudo apt-get update
sudo apt -y install python3-pip
echo '4. Installing packages...'
sudo pip3 install -r ~/CreditSense/bank_node/requirements.txt
echo '5. Installing multichain...'
cd ~/tmp
wget https://www.multichain.com/download/multichain-1.0.4.tar.gz
tar -xvzf multichain-1.0.4.tar.gz
cd multichain-1.0.4
sudo mv multichaind multichain-cli multichain-util /usr/local/bin
cd ~
echo '6. Connecting to multichain chain...'
multichaind chain1@$1 -daemon
echo '7. Setting up local credentials for multichain...'
port=`sudo grep default-rpc-port ~/.multichain/chain1/params.dat | grep -oP '[0-9]{4}'`
networkport=`sudo grep default-network-port ~/.multichain/chain1/params.dat | grep -oP '[0-9]{4}'`
password=`sudo grep rpcpassword  ~/.multichain/chain1/multichain.conf | cut -d'=' -f2`
ml_host=$1
cat >~/CreditSense/bank_node/API/credentials.json <<EOF
    {
      "ml_host": "${ml_host%%:*}",
      "rpcuser": "multichainrpc",
      "rpcpasswd": "$password",
      "rpchost": "localhost",
      "rpcport": "$port",
      "chainname": "chain1",
      "mlport":"5000"
    }
EOF
echo '8. Opening ports....'
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 5000
sudo ufw allow $networkport
sudo ufw --force enable
address=`multichain-cli chain1 getaddresses | grep '"' | cut -d '"' -f2`
echo "Get 60% consensus from the network to grant admin permissions to your address $address"
echo '9. Starting flask server...'
cd ~/CreditSense/bank_node/API
python3 app.py $address &
echo '10. Starting frontend...'
sudo apt-get install -y nodejs
sudo apt-get install -y npm
cd ~/CreditSense/frontend
npm install
sudo npm start &
