---
layout: post
title: "Gerenciando Bare Metal com Metal As a Service (MaaS)"
date: 2017-08-21 18:56:10 -0300
comments: true
categories: maas ubuntu bare metal canonical
---

![](/images/maas/maaslogo.png)

Que tal gerenciar seus Bare Metal com automação e eficiência? Te apresento o Metal as a Service (MaaS) uma ferramenta fantástica desenvolvida em Python pela Canonical que trás vários benefícios para gerenciar seus racks de Bare Metal e neste artigo irei falar um pouco das suas funções, instalação e configuração.

Segue abaixo algumas features do MaaS stable(2.2):

  - Suporte para Bare Metal (ARM,Intel), KVM, VMWARE
  - Provisiona com Ubuntu, RHEL, CENTOS, SLES, OpenSUSE, Windows
  - Divide recursos por zonas Bare Metal/VM
  - IPAM coleção de Subnets IPV4/IPV6, VLAN tagging, DNS, proxy, NTP
  - REST API intregraçao com ferramentas de Devops Juju, Chef, Ansible, Puppet
  - Descobre automaticamente ativos de redes, VLAN, Subnets etc..
  - Enlist automático por PXE 
  - Interface GUI e CLI para Ligar/Desligar, comissionar, implantar, teste de hardware, modo de manutenção e recuperação de S.O
  - Composição Dinâmica de Hardware por meio de POD Suporta Intel Rack Scale Design (RSD) e Virsh(KVM)
  - Configuração de Rede IP,VLAN,BOND,BRIDGE layout de disco Bcache, RAID, LVM

  O MaaS foi desenvolvido para ambientes em escala Bare Metal,  mais também é possível gerenciar VM com Virsh(KVM). Suporta as  principais BMCs e controladores de chassi do mercado como IBM, Lenovo, Disco, Huawei, Dell, HP e Open Compute Project, está sendo utilizado por grandes plays do mercado como Microsoft, Nec, Verizon, At&t, NTT atualmente sendo considerado uma das melhores ferramentas open source para gerenciamento de Bare Metal.

#Como funciona

O MaaS possui uma arquitetura em camadas com um banco de dados postgresql usado na 'Region Controller (regiond)' que lida com as solicitações. Já o Distributed Rack Controllers (rackd) fornecem serviços para cada rack. 

Region controller(regiond):

   - REST API server (TCP port 5240) 
   - PostgreSQL database 
   - DNS 
   - caching HTTP proxy 
   - Web GUI 


Rack Controller (rackd) fornece DHCP, IPMI, PXE, TFTP e outros serviços locais. Os rackd armazenam itens  como imagens de instalação do S.O no nível do rack para melhor desempenho, mas não mantenham nenhum estado além das credenciais para falar com o Region Controller.

Rack controller(rackd):
  
   - DHCP 
   - TFTP 
   - HTTP (para images) 
   - iSCSI 
   - Power Management 

Tanto o regiond como o rackd podem ser escalados e configurados para alta disponibilidade.

![](/images/maas/archmaas.png)

#Instalando o MaaS

Como podemos ver na arquitetura acima, em cada rack de servidor Bare Metal poderiamos ter um daemon chamado rackd que falaria via API com o regiond, isso e uma boa pratica para arquitetura de rede Layer 3 spine e leaf, mas neste exemplo vamos instalar tanto o regiond como o rackd em um unico servidor.

Adicionando repositorio e instalando o MaaS

```bash
# apt-add-repository -yu ppa:maas/stable
# apt install maas
```

Após instalação precisamos criar um usurário administrativo.

```bash
# maas createadmin 
```

Depois da criação vamos acessar o painel via browser

** Acesse a URL:http://$API_HOST:5240/MAAS **

Entre com login e senha criado no passo anterior

![](/images/maas/maaslogin.png)

No primeiro login será apresentado uma tela de configuração, altere o nome da sua região se achar necessário e neste primeiro momento deixe como padrão os outros valores

Obs: para o MaaS conseguir Ligar e Desligar os servidores via IPMI será necessário um interface que chegue na rede da  IDRAC e/ou ILO

![](/images/maas/maasfist.png)

Agora vamos verificar quais serviços estão ativos, no painel click em “Nodes” selecione a aba “Controller” selecione o servidor da sua controller depois click na aba “Services”.
![](/images/maas/maasservices.png)

Veja se sua img está sincronizada Click na Aba “Images” 

![](/images/maas/maasimage.png)

- Ativando DHCP


Vá para a aba "Subnets" e selecione a untagged VLAN/subnet  para a qual você deseja habilitar o DHCP, e no botão "Take action" selecione "Provide DHCP".

  - Defina o controlador de rack que gerenciará o DHCP.
  - Selecione a subrede para criar o intervalo dinâmico DHCP.
  - Preencha os detalhes para o intervalo dinâmico.

![](/images/maas/maasnetwork.png)

Após ativar o DHCP, podemos inciar os bare mental na rede configurada que automaticamente ela realizará o boot via PXE e iniciará o processo de enlist, assim aparecendo no menu “Node” do painel MaaS, abaixo veja como funciona o ciclo de vida do seu Bare Metal/VM dentro do MaaS.

#Entenda o Lifecycle do MaaS

Cada máquina ("nó") gerenciada pelo MAAS passa por um ciclo de vida desde o alistamento até o comissionamento quando o nó será inventariado e iremos poder configurar elementos específicos do hardware. No ciclo também é possível alocamos um servidor para um usuário, realizar o deployer, e finalmente liberar de volta para um pool ou deletar por completo.

![](/images/maas/maaslifecycle.png)


** Qualquer dúvida comentem aííí, até a proxima!!!! **

Referências: 

https://maas.io/

https://docs.ubuntu.com/maas/