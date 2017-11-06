---
layout: post
title: "Um pouco sobre o Ceph Day SP 2017"
date: 2017-10-27 12:09:02 -0200
comments: true
categories: ceph cephdaysp evento ceph luminous
---

![](/images/ceph/cephday0.png)

Na última Quarta-feira(25/10) rolou o primeiro Ceph Day SP e o primeiro na América Latina organizado e realizado pelo nosso Manager Comunity Leonado Vaz e nosso amigo da Savant Marcos Sungaila, além de grandes patrocinadores como RedHat, Canonical, Suse entre outros...

Para quem não teve a oportunidade de estar presente perdeu um grande dia. Discutimos sobre a nova versão do Ceph, custos x performance, implementações, cases e principalmente o futuro do SDS

![](/images/ceph/cephday1.png)

A chegada da nova versão Luminous LTS que já é uma realidade, virou um divisor de águas no mundo do Software Define Storage(SDS) com várias melhorias como o novo backend BlueStorage que leva o Ceph a um nível de performance 2x mais rápido eliminando a camada do filesystem, além de grandes melhorias em toda sua estrutura. 

Precisando de baixa latência e alta performance? O Ceph te entrega, tivemos uma palestra da Intel, uma das grandes colaboradoras do código, falando sobre Ceph com All-Flash.

[SSDs to Build High-Performance Cloud Storage Solutions](https://software.intel.com/en-us/articles/using-intel-optane-and-intel-3d-nand-technology-with-ceph-to-build-high-performance-cloud)


Para os amantes do Zabbix como eu, o novo serviço de gerenciamento do Ceph(ceph-mgr) foi ampliado com vários módulos python, um deles exporta o status geral do cluster para o Zabbix habilitando o modulo no Ceph e configurando o template no zabbix.

```bash
$ ceph zabbix config-set zabbix_host zabbix-server.local
$ ceph zabbix config-set identifier ceph.local
```

Para os amantes da interface GUI. Agora será possível ter um dashboard no Ceph de forma simples. 

```bash
$ ceph mgr module enable dashboard
```
Acesse http://you_active_mgr_host:7000/

![](/images/ceph/cephday2.png)
![](/images/ceph/cephday3.png)

Outra grande novidade, agora já é possível fazer Erasure Coding tanto em RBD quanto em CephFS, que antes só era possível com object. Na mudança para o BlueStorage será possível suporta compressão de dados, trazendo mais economia no armazenamento. 

E tem muito mais vindo por ai! Eu particularmente estou ansioso para o tão esperado QoS que está por vir na próxima versão ou dedup que será excelente para galera de backup. Aguardem que isso será só o começo da evolução que o Ceph vem trazendo para o mundo do Software Define Storage.

Referências:

http://ceph.com/releases/v12-2-0-luminous-released/

http://ceph.com/community/new-luminous-dashboard/

http://ceph.com/community/new-luminous-zabbix/