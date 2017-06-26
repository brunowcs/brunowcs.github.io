---
layout: post
title: "Redimensionar disco no VMware com LVM utilizando RHEL/CentOS - On the Fly"
date: 2016-06-22 09:30:26 -0300
comments: true
categories: linux rhel centos lvm vmware
---

Uma das demandas que executo diariamente está relacionado a expansão de disco em máquinas virtuais. Muitas vezes a máquina não pode ser reiniciada e todo procedimento precisa ser executado em produção.

> Sempre execute um snapshot da VM antes de executar os procedimentos abaixo.

Primeiro passo temos que aumentando nosso disco, no Vmware.

Selecione a VM no seu vSphere depois, vá em “Edit Settings”, selecione o “Virtual Disk” que deseje aumentar. No meu caso aumentarei 20G. 

Verificando as partições do sistema:

    
    # df -h

    FilesystemSize  Used Avail Use% Mounted on
    /dev/mapper/vg_web01-lv_root 45G  1.5G   42G   4% /
    tmpfs 1.9G 0  1.9G   0% /dev/shm
    /dev/sda1 477M   78M  374M  18% /boot

Partição que sera expandida (**/dev/mapper/vg_web01-lv_root**)

Todo procedimento será realizado com a VM ligada e a partição montada.

Vamos agora realizar um procedimento para que o seu Linux reconheça o novo espaço adicionado sem precisar do reboot.


    # ls /sys/class/scsi_device/
    0:0:0:0    2:0:0:0 
    # echo 1 > /sys/class/scsi_device/0\:0\:0\:0/device/rescan
   

No meu caso tenho duas controladoras e meu disco se encontra na primeira. Pronto agora quando for executar o cfdisk ou fdisk você já consegue visualizar o espaço adicionado no Vmware, no meu caso foi criado o /dev/sda3.

> Caso seja um novo Virutal Disk, execute os comando abaixo para identificar o novo device no seu ambiente sem precisar realizar o reboot. 
> 
>
	Buscando host bus number
	# grep mpt /sys/class/scsi_host/host?/proc_name
	/sys/class/scsi_host/host0/proc_name:mptspi
>		
	Execute o comando abaixo no host encontrado
    # echo "- - -" > /sys/class/scsi_host/host0/scan


Vamos utilizar o cfdisk para criar uma nova partição com o espaço disponível do tipo LVM(8e)

    # cfdisk /dev/sda3 (a utilização do cfdisk não será abordada passo-a-passo)

![cfdisk]({{ site.url }}/images/cfdisk.JPG)

Após a criação da nova partição, execute o comando abaixo

    # partprobe /dev/sda (RHEL7)
    # partx -a /dev/sda (RHEL6)

Podemos visualizar com o comando abaixo a nova partição reconhecida pelo sistema chamada **sda3** 
   
     # cat /proc/partitions

    major minor  #blocks  name
    
       80   73400320 sda
       81     512000 sda1
       82   51915776 sda2
       83   20971520 sda3
     2530   47849472 dm-0
     25314063232 dm-1

Após a nova partição ser reconhecida vamos adiciona ao LVM.

    # pvcreate /dev/sda3	

    Physical volume "/dev/sda3" successfully created 

Expandindo grupo vg_web01

    # vgextend vg_web01 /dev/sda3

    Volume group "vg_web01" successfully extended

Expandindo Partição vg_web01-lv_root


    # lvextend -L+20GB /dev/mapper/vg_web01-lv_root

      Size of logical volume vg_web01/lv_root changed from 45.63 GiB (11682 extents) to 65.63 GiB (16546 extents).
      Logical volume lv_root successfully resized.

Redimensionar sistema de arquivo ext4

   	# resize2fs /dev/vg_web01/lv_root

	resize2fs 1.41.12 (17-May-2010)
	Filesystem at /dev/vg_web01/lv_root is mounted on /; on-line resizing required
	old desc_blocks = 3, new_desc_blocks = 5
	Performing an on-line resize of /dev/vg_web01/lv_root to 16943104 (4k) blocks.
	The filesystem on /dev/vg_web01/lv_root is now 16943104 blocks long.

Podemos agora verificar que a partição foi redimensionada para 65G sem precisar reiniciar ou muito menos desmontar.

	# df -h
	FilesystemSize  Used Avail Use% Mounted on
	/dev/mapper/vg_web01-lv_root 65G  1.5G   59G   3% /
	tmpfs 1.9G 0  1.9G   0% /dev/shm
	/dev/sda1 477M   78M  374M  18% /boot

Caso sua partição seja xfs basta executar o seguinte comando

    # xfs_growfs /dev/vg_web01/lv_root


##### Referências:

- http://tldp.org/HOWTO/LVM-HOWTO/index.html

- https://blogs.it.ox.ac.uk/oxcloud/2013/03/25/rescanning-your-scsi-bus-to-see-new-storage/