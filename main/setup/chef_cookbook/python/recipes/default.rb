#
# Author:: Seth Chisamore <schisamo@opscode.com>
# Cookbook Name:: python
# Recipe:: default
#
# Copyright 2011, Opscode, Inc.
#
# Edited:: David Marble <davidmarble@gmail.com>
#   * 2012
#       * version check to decide if source compilation needed
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

def check_minver(minver)
    minver_met = false
    python_bindir = "#{node['python']['prefix_dir']}/bin/"

    begin
        pythonver = `python -V 2>&1`
    rescue
    else
        currver = pythonver.gsub("Python ","").strip().chomp.strip().split('.').join('').to_i
        if currver >= minver
            minver_met = true
            minver_python = `which python`.chomp
            if not minver_python.include?(python_bindir)
                # Make sure a link exists to minver_python in python_bindir.
                # This is necessary because although /usr/bin/python may meet 
                # the minimum version required, when a user installs distribute 
                # and pip, they're placed in /usr/local/bin/.
                bash "link minver python" do
                    cwd python_bindir
                    code <<-EOF
                    if [ -s python ]; then
                        rm python
                    elif [ -f python ]; then
                        mv python python.bak
                    fi
                    ln -s #{minver_python} python
                    EOF
                end
            end
        end
    end

    if not minver_met
        # Check for python already installed from source, because `python` above
        # seems to execute with a custom basic PATH different from the PATH set 
        # for normal interactive logins. You can see this by uncommenting this code:
        # env = `env`
        # raise "#{currver.to_s}-#{minver.to_s}\n#{env}"
        begin
            pythonver = `#{python_bindir}python -V 2>&1`
        rescue
        else
            currver = pythonver.gsub("Python ","").strip().chomp.strip().split('.').join('').to_i
            if currver >= minver
                minver_met = true
            end
        end
    end
    return minver_met
end

minver = node[:python][:min_version].split('.').join('').to_i
minver_met = check_minver(minver)

if minver_met
    # Make sure python-dev installed
    if node[:python][:install_method] == "package"
        include_recipe "python::package"
    end
else
    if node[:python][:install_method] == "package"
        include_recipe "python::package"
        minver_met = check_minver(minver)
    end
end

# Whether source or package, if the minimum version isn't met,
# install via source

if not minver_met
    include_recipe "python::source"
end

include_recipe "python::pip"
include_recipe "python::virtualenv"
if node[:python].attribute?("WORKON_HOME")
    include_recipe "python::virtualenvwrapper"
end