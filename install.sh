sudo apt-get install -y python-pip
sudo pip install --upgrade pip
sudo pip install virtualenv
virtualenv -p python3 ~/algorand-env
printf "\nalias algorand_env='source /home/$USER/algorand-env/bin/activate'" >> ~/.bash_aliases
source ~/.bashrc
source /home/$USER/algorand-env/bin/activate
pip install -r requirements.txt