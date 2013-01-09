include_recipe "apt"
include_recipe "apache2"
#include_recipe "python"
include_recipe "mongodb::default"

#virtualenv_dir = "/app/python"

#python_virtualenv virtualenv_dir do
#    interpreter "python"
#    action :create
#end

#python_pip "web.py" do
#  action :install
#  virtualenv virtualenv_dir
#end

#python_pip "httplib2" do
#  action :install
#  virtualenv virtualenv_dir
#end

#python_pip "pymongo" do
#  action :install
#  virtualenv virtualenv_dir
#end

#python_pip "Genshi" do
#  action :install
#  virtualenv virtualenv_dir
#end