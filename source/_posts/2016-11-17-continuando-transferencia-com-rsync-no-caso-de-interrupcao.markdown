---
layout: post
title: "Continuando transferência com RSYNC no caso de interrupção"
date: 2016-11-17 13:38:43 -0200
comments: true
categories: linux rsync
---

![rysnc](/images/rsync.jpg)

Olá turmadaaa, precisei realizar uma transferência de uma VM do XenServer com 300G que estava em um ponto de montagem NFS para um outro local remoto e para evitar problemas de interrupção, utilizei o comando abaixo que me permiti continuar a transferência em casos de problemas, como perda de conexão etc...


    # rsync -vrlPtz --append /mnt/web.xva /storage/export/
    	sending incremental file list
    	web.xva 	4641783808   1%   6.89MB/s    9:57:11
     	 
O Comando acima basicamente irá comprimir, continuar e salvar parcialmente apresentando a saída em detalhes. Pode ser utilizado com apenas um arquivo ou com diretórios.


Caso queira usar com ssh:

    # rsync -vrlPtz --append -e 'ssh -p 2222' login@host:/tmp/web.xva /tmp/web.xva

Dica SSH Com Tunnel: ssh -L 2222:hostlocal:2222 root@hostremoto
	
	
	
----------

**Referência:**

https://download.samba.org/pub/rsync/rsync.html