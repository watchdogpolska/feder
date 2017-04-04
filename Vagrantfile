# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.

#!/usr/bin/env bash

Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "bento/ubuntu-16.04"

  config.vm.define "mgmt" do |web|
    web.vm.network "private_network", ip: "192.168.33.10"
    web.vm.network :forwarded_port, guest: 22, host: 2210
    web.vm.network :forwarded_port, guest: 8000, host: 8000
    web.vm.provider "virxtualbox" do |vb|
        vb.memory = 1024 + 512
    end
    web.vm.provision :ansible do |ansible|
      ansible.playbook = "vagrant_provision_ansible.yaml"
    end
  end

end
