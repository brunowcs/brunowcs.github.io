---
layout: post
title: "Migrando VM XenServer para Ovirt/RHEV/KVM"
date: 2016-11-25 11:24:55 -0200
comments: true
categories: xen xenserver kvm linux
---
![](/images/ovirt/migracao.png)

Depois de 4 anos utilizando XenServer, chegou a hora de dá um até breve. Atualmente estou migrando alguns ambientes XenServer para Ovirt/KVM pela sua constante evolução e integração com o projeto Openstack que vem crescendo muito no cenário opensource.

Primeiro passo será exporta sua VM pelo XenCenter ou pelo seu node console conforme o comando abaixo.

	# xe vm-export vm=<Name of VM> filename=<Name of file ending in ".xva">


Será gerado uma imagem com extensão .xva, jogue sua imagem exportada para seu node ovirt.

Desempacotando VM.

    # tar -xvf vm.xva

No meu ambiente foi criado um diretório chamado Ref\:10/



Baixe o script de migração (https://github.com/hswayne77/xenserverz\_to\_xen)

	# wget wget https://raw.githubusercontent.com/hswayne77/xenserver_to_xen/master/xenmigrate_new.py


Execute os comandos para iniciar a migração da imagem.

	
    # python xenmigrate.py -c Ref\:10/ vm.img

    enmigrate 0.7.4 — 2011.09.13
    (c)2011 Jolokia Networks and Mark Pace — jolokianetworks.com
    
    convert ref dir : ./Ref:10/
    to raw file : vm.img
    last file : 20484
    disk image size : 20 GB
    
    RW notification every: 1.0GB
    Converting: 1.0GBrw 2.0GBrw 3.0GBrw 4.0GBrw 5.0GBrw 6.0GBrw 7.0GBrw 8.0GBrw 9.0GBrw 10.0GBrw 11.0GBrw 12.0GBrw 13.0GBrw 14.0GBrw 15.0GBrw 16.0GBrw 17.0GBrw 18.0GBrw 19.0GBrw 20.0GBrw
    Successful convert

Criando Domain Storage Export no Ovirt

Acesse no browse seu Ovirt Engine vá para:
 
**Sistema -> Data Centers -> Default -> Storage -> Novo Domain**

Crie um novo Dominio "Export" conforme a imagem abaixo.

![](/images/ovirt/exportstorage.JPG)


Baixe a última versão do projeto "import-to-ovirt.pl" no seguinte link http://git.annexia.org/?p=import-to-ovirt.git

Instale as dependências

	# yum install perl-XML-Writer perl-Sys-Guestfs
	
Agora vamos importa a vm.img para o Domain Export que criamos utilizando o import-to-ovirt.pl

	
	# export LIBGUESTFS_BACKEND=direct
	# ./import-to-ovirt.pl vm.img node1.supcom:/storage/export

> Pode ser utilizado com imagem .qcow2
  
Verifique se tudo ocorreu bem com a criação do OVF

    [root@node1 storage]# ls /storage/export/ad5e39a2-24d4-4a51-ac74-cfdf843c5f94/master/vms/88397ea1-196e-4aeb-8a57-29cff914caab/88397ea1-196e-4aeb-8a57-29cff914caab.ovf


Disponbilizando a VM no Ovirt Engine

Sistema -> Data Centers -> Default -> Cluster -> Default - > MVS -> Importar”:

![](/images/ovirt/ovirtimport.JPG)

Selecione o Export Domain criado, click em Carregar, Seleciona a VM, click na seta central, depois Próximo.

![](/images/ovirt/ovirtimport2.JPG)

Click OK e aguarde a VM ser importada.

**Após a importação será necessário realizar algumas alterações no momento da inicialização da VM:**


- Pressione "e" na inicialização do grub remova o "console=hvc0" e digite CTRL + X 

**Após a inicialização**

- Remova o "console=hvc0" /etc/default/grub e execute:

	    # update-grub


- Verifique se seu fstab está correto e não tenha entradas xvda

- Verifique sua network os uuid e MAC serão diferentes.

- Edite o /etc/inittab comente a linha “co:2345:respawn:/sbin/getty ... ”:



> A vm migrada estava com Debian 7 e a migração foi executada com sucesso seguindo os procedimentos acima  

**Referências:**

https://gfnork.de/blog/how-to-import-qcow2-images-to-ovirt/

https://rwmj.wordpress.com/2015/09/18/importing-kvm-guests-to-ovirt-or-rhev/

http://blog.zwiegnet.com/linux-server/export-vm-command-line-xenserver-6/

https://wiki.debian.org/HowToMigrateBackAndForthBetweenXenAndKvm