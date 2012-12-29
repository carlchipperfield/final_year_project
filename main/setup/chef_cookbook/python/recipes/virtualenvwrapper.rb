include_recipe "utils::disable_hg_cert_checking"

# Ensure WORKON_HOME_owner exists
utils_ensure_user node[:python][:WORKON_HOME_owner] do
    update_if_exists false
end

# Ensure WORKON_HOME_group exists
utils_ensure_group node[:python][:WORKON_HOME_group] do
    members [node[:python][:WORKON_HOME_owner]]
end

# Create WORKON_HOME
directory node[:python][:WORKON_HOME] do
    action :create
    owner node[:python][:WORKON_HOME_owner]
    group node[:python][:WORKON_HOME_group]
    mode node[:python][:WORKON_HOME_group_writeable] ? "2775" : "775"
    recursive true
end

# If it should be group-writeable, use ACL
# Change ownership of WORKON_HOME to WORKON_HOME_owner:WORKON_HOME_group
# chmod 2775 on all WORKON_HOME directories
# chmod ug+rw (add user and group read/write) on all WORKON_HOME directories
# Find files executable by owner,group,anyone and make them writable by www-pub
# Find files not executable by anyone and make them rw by www-pub
if node[:python][:WORKON_HOME_group_writeable]
    utils_acl node[:python][:WORKON_HOME]
    bash "set default ACLs and fix existing perms on #{node[:python][:WORKON_HOME]}" do
        code "/usr/local/bin/fixperms #{node[:python][:WORKON_HOME_owner]} #{node[:python][:WORKON_HOME_group]} #{node[:python][:WORKON_HOME]}"
    end
end

python_pip "virtualenvwrapper" do
  action :install
end

# Force an initialization of virtualenvwrapper
script "Initialize virtualenvwrapper" do
    interpreter "bash"
    user "root"
    cwd Chef::Config[:file_cache_path]
    code <<-EOH
su -p -l -c 'echo' root
    EOH
end

# Old way on ubuntu
# script "Install davidmarble's virtualenvwrapper" do
    # interpreter "bash"
    # user "root"
    # cwd Chef::Config[:file_cache_path]
    # This location is Debian-specific:
    # code <<-EOH
    # pip install --src=$(python -c \"import os, sys; print os.path.join('/usr/local/lib', 'python' + sys.version[:3], 'dist-packages')\") -e hg+https://bitbucket.org/davidmarble/virtualenvwrapper#egg=virtualenvwrapper
    # EOH
    # not_if { ::FileTest.exists?("/usr/local/bin/virtualenvwrapper.sh") }
# end
