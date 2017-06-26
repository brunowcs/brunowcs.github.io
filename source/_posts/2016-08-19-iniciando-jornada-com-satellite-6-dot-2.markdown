---
layout: post
title: "Iniciando jornada com Satellite 6.2"
date: 2016-08-19 14:48:46 -0300
comments: true
categories: linux rhel centos satellite
---


Recentemente a Red hat lançou o Satellite 6.2 GA, um produto que ganhou grandes melhorias e novas funcionalidades.


![img1](/images/satellite/img1.jpg)

O Satellite se tornou um produto essencial para gerenciamento de ciclo de vida de sistemas da Red Hat em ambientes físicos, virtuais, nuvens privadas e públicas. A ferramenta apresenta implementação remota e estende a capacidade de gestão de pacotes, configurações, máquinas virtuais, containers, segurança entre grandes outras funcionalidades.

Uma das funcionalidades mais interessante dessa nova versão e o Remote Execute e Job Scheduling utilizando ssh. Agora será possível agenda execuções remotas em todos hosts. O OpenSCAP utilizado para auditoria de segurança, agora já vem instalado junto com o Satellite 6.2, antes precisava ser instalado manualmente. Melhorias no console web ficou notório, também percebi que a interface web está mais rápida.

Então amigos administradores de RHEL/CentOS, se você utiliza o Red Hat Satellite 5 e está pensando em implementar o Satellite 6, pode iniciar sua jornada, o  Satellite 6.2 GA está finalmente atingindo o nível de maturidade necessária para gerir ambientes de pequeno e grande porte. 

# Migração 

Atualmente estou utilizando a versão 6.1 e abaixo vou listar os passos e dificuldades encontradas no meu ambiente para migração do 6.2 GA.

> Não será possível realizar migração de 6.2 Beta para 6.2 GA, antes de iniciar a migração para 6.2 verifique se seu ambiente está atualizado e com a versão 6.1.9. Não se esqueça de realizar o backup do ambiente atual.

Verificando se existe alguma atualização recente. 
Desabilite todos repositórios, deixe apenas os seguintes habilitado: 

    # subscription-manager repos --disable=*
    # subscription-manager repos --enable=rhel-7-server-rpms
    # subscription-manager repos --enable=rhel-7-server-satellite-6.1-rpms
    # yum update
    
> Caso atualize o kernel será necessário reiniciar o sistema  

Após o update do S.O e dos novos pacotes, o satellite já estará com a versão 6.1.9, execute o seguinte comando para finalizar:

    # katello-installer --upgrade
    
    Upgrading...
    Upgrade Step: stop_services...
    Upgrade Step: start_mongo...
    Upgrade Step: migrate_pulp...
    Upgrade Step: start_httpd...
    Upgrade Step: migrate_candlepin...
    Upgrade Step: migrate_foreman...
    Upgrade Step: Running installer...
    Installing Done   [100%] 
    
    [......................................................]
      The full log is at /var/log/katello-installer/katello-installer.log
    Upgrade Step: restart_services...
    Upgrade Step: db_seed...
    Upgrade Step: errata_import (this may take a while) ...
    Upgrade Step: update_gpg_urls (this may take a while) ...
    Upgrade Step: update_repository_metadata (this may take a while) ...
    Katello upgrade completed!



Vamos realizar um check antes de realizar a migração para o 6.2.

    # foreman-rake katello:upgrade_check
    
    This script makes no modifications and can be re-run multiple times for the most up to date results.
    Checking upgradeability...
    
    Checking for running tasks...
    [FAIL] - There are 35 active tasks.
    
    Checking the current version...
    [PASS] - Current version of the Katello Ruby RPM is 2.2.0.92 and needs to greater than or equal to 2.2.0.90
    
    Checking content hosts...
    Calculating Host changes on upgrade.  This may take a few minutes.
    
    
    Summary:
    Content hosts to be preserved: 169
    Content hosts to be deleted: 3
    Details on Content Hosts planned for deletion saved to /tmp/pre-upgrade-1471033031.csv
    You may want to manually resolve some of the conflicts and duplicate Content Hosts.
    Upon upgrade those found for deletion will be removed permanently.


Como podemos ver minha migração apresentará falha **" [FAIL] - There are 35 active tasks."** Resolvendo active tasks provável lock, podemos ir manualmente na Web gui Monitor->Tasks e filtrar pelas tasks que estão em lock, assim executando manualmente os skip, também podemos identificar pelo hammer. 


Apresenta um resumo das tasks em pausa

    # hammer task resume --search "state=paused"

Apresenta todas tasks em pausa

    # hammer task list --search "state=paused"

Removendo tasks em lock pelo foreman-rake
     
	# service foreman-tasks stop  
    # foreman-rake console
	
    irb(main):001:0> ForemanTasks::Task.where(:state => :planned).where(:label => "Actions::Katello::Repository::Sync").destroy_all
    irb(main):002:0> ForemanTasks::Task.where(:state => :planned).where(:label => "Actions::Katello::System::GenerateApplicability").destroy_all
    irb(main):003:0> ForemanTasks::Task.where(:state => :paused).where(:label => "Actions::Katello::Repository::Sync").destroy_all
    irb(main):004:0> ForemanTasks::Task.where(:state => :paused).where(:label => "Actions::Katello::System::GenerateApplicability").destroy_all
    irb(main):005:0> ForemanTasks::Task.where(:label => "Actions::Candlepin::ListenOnCandlepinEvents").destroy_all
    
	Caso nescessário remova a task pelo id
	irb(main):001:0> ForemanTasks::Task.find("799bc5fb-2d4c-4d0d-9d7d-4e42e9a8ace8").destroy
	
    Saindo do Foreman rake
    irb(main):002:0> exit
	# service foreman-tasks start 
	
Reindexando o banco de dados para evitar futuras inconsistências

    # foreman-rake katello:reindex
	# katello-service restart


Executando novamente o upgrade_check podemos notar que as  pendência de tasks foram solucionadas.

    # foreman-rake katello:upgrade_check
    
    This script makes no modifications and can be re-run multiple times for the most up to date results.
    Checking upgradeability...
    
    Checking for running tasks...
    [PASS] - There are 0 active tasks.
    
    Checking the current version...
    [PASS] - Current version of the Katello Ruby RPM is 2.2.0.92 and needs to greater than or equal to 2.2.0.90
    
    Checking content hosts...
    Calculating Host changes on upgrade.  This may take a few minutes.
    
    
    Summary:
    Content hosts to be preserved: 169
    Content hosts to be deleted: 3
    Details on Content Hosts planned for deletion saved to /tmp/pre-upgrade-1471269446.csv
    You may want to manually resolve some of the conflicts and duplicate Content Hosts.
    Upon upgrade those found for deletion will be removed permanently.
    

# Iniciando processo de upgrade 6.2 #

 
Desabilitar repositório Satellite 6.1

    # subscription-manager repos --disable rhel-7-server-satellite-6.1-rpms

Habilitando repositórios necessário

    # subscription-manager repos --enable rhel-7-server-satellite-6.2-rpms

    # subscription-manager repos --enable=rhel-server-rhscl-7-rpms


Parando serviço

    # katello-service stop

Limpando cache yum

    # yum clean all
    
Upgrade de todos pacotes do sistema

    # yum update

Upgrade do ambiente satellite


    # satellite-installer --scenario satellite --upgrade

Nessa etapa acima encontrei um erro de migração que estava relacionado a ambiente puppet orfão, caso ocorra um erro parecido, tente remove o ambiente puppet informado na msg e execute o comando novamente.

> foreman-rake katello:upgrades:3.0:update_puppet_repository_distributors
Updating Puppet Repository Distributors
Updating Content View Puppet Environment Distributors
rake aborted!
ForemanTasks::TaskError: Task 541787f6-ad56-449a-be6f-1b2001fc3538: Katello::Errors::PulpError: PLP0034: The distributor Library-ccv_rhel72_puppet-jboss indicated a failed response when publishing repository **Library-ccv_rhel72_puppet-jboss**.


Iniciando serviço

    # katello-service start


Verificando serviço

    # hammer ping
	candlepin:
    Estado:          ok
    Server Response: Duration: 19ms
	candlepin_auth:
    Estado:          ok
    Server Response: Duration: 23ms
	pulp:
    Estado:          ok
    Server Response: Duration: 66ms
	foreman_tasks:
    Estado:          ok
    Server Response: Duration: 882ms

Verique também na interface web se todos os serviços estão ok, na aba Administer->About

Caso ao logar na interface Web, apresente um erro de "undefined method `label' for nil:NilClass" atualize o pacote tfm-rubygem-katello e reinicie o serviço. (https://bugzilla.redhat.com/show_bug.cgi?id=1361793)

![img2](/images/satellite/img2.jpg)



	# rpm -Uvh tfm-rubygem-katello-3.0.0.73-1.el7sat.noarch.rpm
	# katello-service restart


![img3](/images/satellite/img3.jpg)		
	
# Upgrade Client Satellite 6.2 #


Desabilite repositório antigo

    # subscription-manager repos --disable rhel-7-server-satellite-tools-6.1-rpms

Habilite novo repositório

    # subscription-manager repos --enable=rhel-7-server-satellite-tools-6.2-rpms


Realize upgrade do katello-agent

    # yum upgrade katello-agent


# Referencias: #

- https://access.redhat.com/blogs/1169563/posts/2464761

- https://access.redhat.com/documentation/en/red-hat-satellite/6.2/single/installation-guide
