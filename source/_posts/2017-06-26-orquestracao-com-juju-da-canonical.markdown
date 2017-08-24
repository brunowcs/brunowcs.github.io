---
layout: post
title: "Orquestração com Juju da Canonical"
date: 2017-06-26 18:14:34 -0300
comments: true
categories: juju, lxd, linux, canonical, ubuntu 
---

![](/images/juju/juju1.png)

### O que é o Juju? ###

Juju é uma ferramenta open source de modelagem de aplicações desenvolvida em Go pela Canonical a mesma empresa que desenvolve o Linux Ubuntu. 

Com Juju é possível  implementar, configurar, gerenciar, manter e dimensionar aplicações em nuvens públicas e privadas de uma forma rápida e eficiente bem como servidores físicos,  OpenStack e contêineres. O Juju pode ser usado tanto em linha de comando ou através de uma interface GUI

### Como é feito a “Mágica”: ###

A partir dos charmes é possível realizar a criação de toda uma infraestrutura no nivel de configuração da maquina virtual, instalação e configuração das aplicações, interligações de dependências, tanto na AWS, Google, Azure, OpenStack entre outras nuvem suportadas ou diretamente no Bare-Metal.

### Mas que desgraça é esse Charme? ###

O charme define tudo o que você conhece de forma colaborativa sobre a implantação da aplicação. Tudo o que você precisa fazer é usar qualquer charme disponível (ou escrever o seu próprio), e a aplicação correspondente será implantada em segundos, em qualquer nuvem, servidor físico ou máquina virtual.

O Charme nada mais é do que um receita de instalação e configuração com gerenciamento de dependencias e interligações nescessárias para sua aplicação funcionar em uma nuvem ou em um bare-metal.

### Juju então é igual ao Chef, Puppet, Ansible e cia? ###

Não! O Juju orquestra e escala aplicações em nuvens, ele está uma camada acima dos gereciadores de configurações, mas podemos usar todos juntos perfeitamente.

O puppet, Chef e Ansible são ótimas ferramentas para escrever arquivos de configuração. Por trabalhar uma camada acima, o Juju concentra-se nas operações de longo prazo necessárias para manter esse software em execução ao longo do tempo, independentemente da máquina na qual ele está sendo executado. O charme do Juju para um aplicativo inclui (entre outras coisas) toda a lógica para escrever arquivos de configuração para as aplicações, essa lógica em si pode ser escrita em qualquer linguagem ou ferramenta que o desenvolvedor do charme preferi.

É comum que as pessoas comecem a criar um charme juntando Puppet ou Chef ou outros scripts que eles atualmente usam para automatizar a configuração do ambiente. Se o charme vai estar escrevendo e atualizando a configuração para o aplicativo, e já existem ferramentas para abstrair esse arquivo de configuração na sua linguagem preferida (Puppet,Ansible, etc...), então use isso no charme! 

Como podemos ver o Juju consegue reunir várias ferramentas de  automação, deixando você livre para criar seus charme com suas receitas e ferramentas favoritas, ainda melhor, dois charmes diferentes de diferentes equipes que usam ferramentas diferentes trabalharão felizes juntos para implantar uma solução. 

![](/images/juju/juju2.png)


### Veja como é fácil instalar o Juju no Ubuntu Xenial ###

Para fins de teste vamos instalar o juju com o LXD, que no caso poderia ser uma nuvem ou um bare-metal

    $ sudo apt install lxd zfsutils-linux

Para usar o LXD, seu usuário deve ser um membro do grupo lxd, verifique com o comando abaixo provavelmente já vai estar.

    $ groups

Ao executar o comando abaixo, aceite todas respostas padrão nas configurações iniciais do LXD, ou mude caso achar melhor.

    $ sudo lxd init 

LXD agora está basicamente configurado para funcionar com Juju.

### Instalando JUJU: ###

    $ sudo add-apt-repository --update ppa:juju/stable
    $ sudo apt install juju


Tanto para LXD, Bare-Metal ou nuvem será necessário a criação de um controle para gerenciar.

    # juju bootstrap localhost lxd-test 

Isso pode demorar alguns minutos, pois o LXD deve baixar uma imagem do linux.

Uma vez concluído o processo, veja se o controlador lxd-test foi criado com o comando abaixo:

    # juju controllers 

O comando a seguir mostra o controlador, modelo e o usuário atualmente ativo:

    #  juju whoami 

Implantando um aplicativo com Juju. 

O comando abaixo vai até o Juju store pega um charme pronto chamado mediawiki-single e manda instalar no ambiente LXD que configuramos no inicio.

    # juju deploy cs:bundle/mediawiki-single 

Após este comando, podemos verificando sua implementação:

    # juju status

Comando de acesso ao ambiente criado
    
    # juju ssh id_machine

Acesso GUI, o comando abaixo exibirá a URL de acesso a interface web do Juju.
    
    # juju gui

Pegando a senha da controladora criada para logar no Juju Gui.
    
    # juju show-controller --show-password

Mais comandos do Juju.

    # juju help commands


Caso não queira realizar a instalação, a canonical disponibilizou um demo da sua interface GUI: https://demo.jujucharms.com/

Nos próximos posts irei apresentar: 

[ - Juju com Cloud OpenStack ](http://brunocarvalho.net/blog/2017/08/01/palestra-openstack-day-sp-2017/)

[- MaaS para integração do Juju com Bare-Metal ](http://brunocarvalho.net/blog/2017/08/21/gerenciando-bare-metal-com-metal-as-a-service-maas/)

-Deployando Ceph com Juju.


### Referências ###

https://jujucharms.com/docs/stable/


