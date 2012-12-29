#
# Author:: Seth Chisamore <schisamo@opscode.com>
# Cookbook Name:: python
# Recipe:: pip
#
# Copyright 2011, Opscode, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

python_bindir = "#{node['python']['prefix_dir']}/bin/"

# Ubuntu's python-setuptools, python-pip and python-virtualenv packages
# are broken...this feels like Rubygems!
# http://stackoverflow.com/questions/4324558/whats-the-proper-way-to-install-pip-virtualenv-and-distribute-for-python
# https://bitbucket.org/ianb/pip/issue/104/pip-uninstall-on-ubuntu-linux
remote_file "#{Chef::Config[:file_cache_path]}/distribute_setup.py" do
  source "http://python-distribute.org/distribute_setup.py"
  mode "0644"
  not_if { ::File.exists?(python_bindir+'pip') }
end

bash "install-pip" do
  cwd Chef::Config[:file_cache_path]
  # Problems with non-interactive logins
  # http://tickets.opscode.com/browse/CHEF-2288
  # Nothing else seemed able to trigger .bashrc properly.
  # See also https://github.com/wijet/chef-sudo/blob/master/lib/chef-sudo.rb
  code <<-EOF
  su -p -l -c '#{python_bindir}python #{Chef::Config[:file_cache_path]}/distribute_setup.py' root
  su -p -l -c '#{python_bindir}easy_install pip' root
  EOF
  not_if { ::File.exists?(python_bindir+'pip') }
end

if node[:python].attribute?("pip_download_cache")
    directory node[:python][:pip_download_cache] do
        owner "root"
        group "root"
        mode "2777"
        recursive true
    end
end

if node[:python].attribute?("pip_packages")
    node[:python][:pip_packages].each do |pip_pkg|
        if pip_pkg.match(/Pillow/) or pip_pkg.match(/PIL/)
            pkgs = value_for_platform(
              ["debian","ubuntu"] => {
                "default" => ["libjpeg62", "libjpeg-dev", "libfreetype6", "libfreetype6-dev", "zlib1g-dev"]
              },
              ["centos","redhat","fedora"] => {
                "default" => ["libjpeg", "libjpeg-devel", "freetype-devel", "zlib-devel"]
              }
            )        
            pkgs.each do |pkg|
                package pkg
            end
        end
        execute "#{python_bindir}pip install #{pip_pkg}" do
            cwd Chef::Config[:file_cache_path]
        end
    end
end
