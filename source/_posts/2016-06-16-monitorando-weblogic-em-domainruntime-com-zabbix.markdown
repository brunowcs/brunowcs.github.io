---
layout: post
title: "Monitorando Weblogic em DomainRuntime com Zabbix"
date: 2016-06-16 13:51:28 -0300
comments: true
categories: linux centos rhel zabbix weblogic
---

Sempre monitorei Jboss com zabbix, mas recentemente recebi uma demanda e encontrei algumas dificuldades que gostaria de compartilhar com a comunidade.
Esse cenário foi feito no RHEL6, Weblogic 11g com jrockit 1.6, zabbix 2.4, porem entendendo o cenário, pode ser customizado para outras versões.

A Oracle tem um servidor Mbean chamado DomainRuntime, que está disponível no AdminServer. Conectando-se nesse servidor é possível coletar todas informações das JVM e do domínio. Assim não será necessário exporta RMI de cada JVM.
 Com essa solução ganha-se tempo de configuração, segurança, melhor administração de itens e gráficos agregados, além de não haver necessidade de abrir porta JMX em nenhuma JVM.
Então, se tenho um domínio com 10 instancias(JVM), será possível apenas com a URL do console admin pegar todos Mbeans desse domínio.


### Servidores MBean em Weblogic ###

O Middleware Weblogic  é composto por três MBeanServers próprios que são exportados via RMI/IIOP como JSR-160. Estes podem ser consultados por meio de nome JNDI como mostra a lista abaixo. Além disso, existe o PlatformMBeanServer que pode ser exportado juntamente MbeanServer do weblogic. 

- **Domain Runtime MBean Server** 
- **Runtime MBean Server**
- **Edit MBean Server**

O MbeanServer que vamos utilizar para buscar toda árvore do domínio weblogic será a Domínio Runtime MBean Servidor (weblogic.management.mbeanservers.domainruntime). Esse Mbean só está disponível na JVM do AdminServer.

##### Ative os seguintes itens abaixo no admin console do Weblogic: #####

    Domínio->Geral->Avançado 
    
    - Servidor MBean de Compatibilidade Ativado
    - Servidor MBean da Plataforma Ativado
    - Servidor MBean da Plataforma Usado
	
![img1](/images/zabbix/img1.png)

Entre em cada JVM e adicione a seguinte linha no argumento que se encontra na aba Inicialização dos servidores

    Domínio->Ambientes->Servidores->”NAME JVM”->Inicialização do Servidor

    -Djavax.management.builder.initial=weblogic.management.jmx.mbeanserver.WLSMBeanServerBuilder

    
![img2]({{ site.url }}/images/zabbix/img2.png)

 
> ***Será necessário reiniciar o AdminServer e as JVM do domínio.***

##### Exportando RMI/IIOP AdminServer #####

Para facilitar a configuração, vamos utilizar a leitura dos Mbeans como anonymous, mas também poderíamos utilizar autenticação fixada no  JNDI.
Permitir anonymous acesso de  leitura, caso deseja monitorar sem autenticação no AdminServer.

 
    Domínio->Segurança->Geral  - Ative o ‘Acesso Anônimo Ativado”

![img3](/images/zabbix/img3.png)

##### Habilitar o IIOP no manager AdminServer #####

    Dominio->Ambientes->Servidores->AdminServer->Protocolos->IIOP 

![img4](/images/zabbix/img4.png)

> ***Será necessário reiniciar o AdminServer.***

Agora abra o jconsole com os seguintes parâmetros:

    jconsole -J- Djava.class.path=$JAVA_HOME/lib/jconsole.jar:$JAVA_HOME/lib/tools.jar$WL_HOME/server/lib/wljmxclient.jar -J-Djmx.remote.protocol.provider.pkgs=weblogic.management.remote

Use a URL de serviço JMX via IIOP DomainRuntime: 

    service:jmx:rmi:///jndi/iiop://IPADMINSERVER:7001/weblogic.management.mbeanservers.domainruntime

Primeiro tente se conectar utilizando o login e a senha do AdminServer e veja se consegue ler a arvore com.bea/DomainRuntimeService. Depois tente sem autenticação e veja se consegue ler via anonymous.

![img5](/images/zabbix/img5.png)

Caso não consiga ler como anonymous vamos alterar a permissão do JNDI.

    1. Entre no AdminConsole(http://IP:7001/), click no AdminServer -> Exibir Árvore JNDI
    2. Vá para o weblogic->management 
    3. Click no mbeanservers 
    4. Click em Segurança->Politicas 
    5. Escolha o Methods= lookup e adicione a politica "Allow access to everyone" 
    6. Restart AdminServer
    7. Abra o jconsole com os parâmetros informados 
    8. Conecte novamente URL : service:jmx:rmi:///jndi/iiop://IPADMINCSERVER:7001/weblogic.management.mbeanservers.domainruntime

![img6](/images/zabbix/img6.png)


##### Modificação do external script jmx_discovery para DomainRuntime #####

Após Conseguir ler a arvore DomainRuntime do AdminServer com jconsole, vamos alterar o external script para realizar as coletas.

External Script original: <a href="https://github.com/RiotGamesMinions/zabbix_jmxdiscovery" target="_blank">github.com/RiotGamesMinions/zabbix_jmxdiscovery</a> 

        
Modificações que foram feita na class JMXDiscovery.java libs adicionadas:


    import java.io.PrintStream;
    import javax.naming.*;
    
    
Alteração na linha 46:

    this.jmxServerUrl = new JMXServiceURL("service:jmx:rmi:///jndi/rmi://" + hostname + ":" + port + "/jmxrmi");
Para:

    this.jmxServerUrl = new JMXServiceURL("service:jmx:rmi:///jndi/iiop://" + hostname + ":" + port + "/weblogic.management.mbeanservers.domainruntime");

Como o DomainRuntime se conecta com IIOP e utiliza algumas libs especificar, foi necessário adicionar o pacote wlfullclient.jar(Pacote encontrado no servidor weblogic)

Coloque o  wlfullclient.jar na pasta lib do pacote zabbix_jmxdiscovery.  Após esses ajustes recompile o pacote utilizando ant. Ao executado o comando será possível acesso a árvore DomainRuntime

> ***Não irei aborta a utilização do [ant](http://ant.apache.org "ant"), pois não e proposito desse post. Futuramente posso está criando um especifico.***

***Obs: O /etc/hosts precisa estar resolvendo o nome da própria máquina local***

Vá para diretório do binário compilado que foi realizado as modificações do jmx_discovery e execute o comando abaixo:

    [brunocarvalho@zabbix zabbix_jmxdiscovery]# ./jmx_discovery com.bea:Name=DomainRuntimeService,Type=* 192.168.10.1:7001
    {"data":[{"{#PROPTYPE}":"weblogic.management.mbeanservers.domainruntime.DomainRuntimeServiceMBean","{#JMXOBJ}":"com.bea:Name=DomainRuntimeService,Type=weblogic.management.mbeanservers.domainruntime.DomainRuntimeServiceMBean","{#JMXDESC}":"<p>Provides a common access point for navigating to all runtime and configuration MBeans in the…

Se a saída for parecida com a de cima seu external script está funcional.

##### Modificação do Zabbix Java Gateway para DomainRuntime #####

Para que o zabbix-java-gateway comece a coletar utilizando o DomainRuntime, será  necessário recompilar o jar do zabbix, alterando a url do jmx na class JMXItemChecker.java.  

Vamos precisar colocar a lib wlfullclient.jar na pasta src para compilar o zabbix-java-gateway

> ***Não irei aborta a compilação do <a href="https://www.zabbix.com/documentation/2.4/manual/installation/install" target="_blank">Zabbix</a>, pois não é proposito deste post. Futuramente posso está criando um especifico.***



Fiz alterações simples para atender minha demanda, mas pode ser melhorada, de uma olhada no seguinte link: <a href="https://support.zabbix.com/browse/ZBXNEXT-1274" target="_blank">support.zabbix.com/browse/ZBXNEXT-1274</a>



**Class alterada:**
*/opt/install/zabbix-2.4.1/src/zabbix_java/src/com/zabbix/gateway/JMXItemChecker.java*


    public JMXItemChecker(JSONObject request) throws ZabbixException
        {
             super(request);
                try
                {
                        String conn = request.getString(JSON_TAG_CONN);
                        int port = request.getInt(JSON_TAG_PORT);
 		 
                        Integer remoting = new Integer("7777");
                        Integer weblogic = new Integer("7001");

                        int retvaljboss = remoting.compareTo(port);
                        int retvalweblogic = weblogic.compareTo(port);
                    if (retvaljboss == 0)
                {
	   //suporta jboss7 na porta jmx 7777        
                    url = new JMXServiceURL("service:jmx:remoting-jmx://" + conn + ":" + port);
                }
                    if (retvalweblogic == 0)
                {
                     url = new JMXServiceURL("service:jmx:rmi:///jndi/iiop://" + conn + ":" + port + "/weblogic.management.mbeanservers.domainruntime");
                }
                  else
                {url = new JMXServiceURL("service:jmx:rmi:///jndi/rmi://" + conn + ":" + port + "/jmxrmi");
                }

Agora sua imaginação não tem limites! Basta configurar seu zabbix para fazer LLD no server Domainruntime do weblogic utilizando o jmx_discovery igualmente como é feito no jmxrmi.

    1. Adicione o host na interface jmx com o ip do AdminConole na porta 7001
    2. Adicione o template weblogic anexo no host
    3. Adicione macro para o host
   
    {$ADMINSERVER} - ipadminserver:7001 
    {$DOMINIO}  - nomedoseudominio

Segue anexo arquivos utilizados: 


<a href="https://github.com/brunowcs/zabbix_weblogic/" target="_blank">github.com/brunowcs/zabbix_weblogic/</a>

O .RAR ficou um pouco grande por conta dos binários java, então tive que dividir em 3 partes para o github aceitar o upload.

- Template Weblogic.xml LLD com 42 itens, 4 triggers, 16 gráficos criado para weblogic DomainRuntime (Não esqueça de configurar as macros)

- JMXDiscovery.jar com alteração da class JMXDiscovery.java do zabbix_jmxdiscovery, recopilação alterações para connect IIOP com inclusão da lib própria do weblogic para comunicação do server Domainruntime

- Bash do jmx_discovery para se colocar junto com o JMX na pasta do externalscripts do zabbix

- zabbix-java-gateway-2.4.1.jar alteração da class  JMXItemChecker.java do zabbix-java-gateway, compilação alterações para connect IIOP com inclusão da lib própria do weblogic comunicação do server  Domainruntime

- wlfullclient.jar (lib utilizada na compilação)

- org-json-2010-12-28.jar (lib utilizada na compilação)

> Recomendo realizar testes no seu em ambiente de teste antes de entrar em produção 

Resultado:

![resultadofinal](/images/zabbix/resultadofinal.png)


