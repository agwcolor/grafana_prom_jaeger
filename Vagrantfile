# -*- mode: ruby -*-
# vi: set ft=ruby :
default_box = "roboxes/opensuse15"


Vagrant.configure("2") do |config|

  config.vm.define "master" do |master|
    master.vm.box = default_box
    #config.vm.box_version = "15.2.31.354"
    master.vm.hostname = "master"
    master.vm.network "private_network", ip: "192.168.33.10", virtualbox__intnet: true
    master.vm.network "forwarded_port", guest: 22, host: 2222, id: "ssh", disabled: true
    master.vm.network "forwarded_port", guest: 22, host: 2000 # Master Node SSH
    master.vm.network "forwarded_port", guest: 80, host: 8080
    master.vm.network "forwarded_port", guest: 9090, host: 9090
    master.vm.network "forwarded_port", guest: 8080, host: 8080
    #master.vm.network "forwarded_port", guest: 8888, host: 8080
    master.vm.network "forwarded_port", guest: 9090, host: 8888
    master.vm.network "forwarded_port", guest: 3000, host: 3000
    master.vm.network "forwarded_port", guest: 3030, host: 3030
    master.vm.network "forwarded_port", guest: 8080, host: 8080
    master.vm.network "forwarded_port", guest: 16686, host: 8088
    #master.vm.network "forwarded_port", guest: 8000, host: 8888
    master.vm.network "forwarded_port", guest: 8888, host: 8888
    master.vm.network "forwarded_port", guest: 8000, host: 8000
    master.vm.network "forwarded_port", guest: 6443, host: 6443 # API Access


    master.vm.provider "virtualbox" do |v|
      v.memory = "4096"
      #vb.memory = "2048"
      v.name = "k3s"
      end
    config.vm.provision "shell", inline: <<-SHELL
      sudo zypper refresh
      sudo zypper --non-interactive install bzip2
      sudo zypper --non-interactive install etcd
      sudo zypper --non-interactive install apparmor-parser
      curl -sfL https://get.k3s.io | sh -
    SHELL
    # config.vm.synced_folder "./", "/vagrant", type: "virtualbox", create: true
  end
end