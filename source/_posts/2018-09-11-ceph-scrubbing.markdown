---
layout: post
title: "Ceph Scrubbing"
date: 2018-09-11 19:03:07 -0300
comments: true
categories: linux ceph sds
---

<span style="display:block;text-align:center">![](/images/ceph/ceph.png) </span>

Olá turmadaaa, um pouco sumido, mas estou de volta com grandes novidades. A pouco mais de 2 anos realizei a implantação de 4 Cluster Ceph com Juju e MaaS na america latina que hoje tem quase 8 Petabyte raw, e quanto mais o cluster crescer, mais ajustes e problemas diferentes aparecem.

Recentemente encontrei um bug relacionado a recuperação de “Placement groups(PGs)” dentro do Jewel. O Ceph não estava conseguindo resolver a inconsistência de uma PG, mesmo executando o “ceph repair” e forçando a passagem do Scrubbing. Pelo que notei nos últimos lançamentos do CEPH tem alguns Bug fix sobre o assunto. 

Esse será o primeiro de alguns posts que irei falar de como resolver manualmente uma pg inconsistente. Primeiramente vamos entender o Scrubbing no Ceph e caso tenha alguma duvida sobre o SDS Ceph não deixa de assitir meu Webinar que postei aqui no Blog [Explorando o Ceph](http://brunocarvalho.net/blog/2018/04/03/webinar-explorando-o-ceph/) Como tiver várias dúvidas sobre Webinar e muitas coisas geraram duvidas, lançarei uma série de artigos com mais detalhes “Explorando o Ceph”.

Podemos comparar o Scrubbing do Ceph com o fsck para o armazenamento de objetos dentro do Cluster.
Ao executar “ceph -s” na ultimas linhas vemos as “placement groups(PGs)” que estão “active+clean” 
Para cada placement groups(PGs) o Ceph gera um catálogo de todos os objetos e compara cada objeto principal e suas réplicas para garantir que nenhum objeto esteja ausente ou seja incompatível.
Muitas vezes vamos achar a seguinte informação “1 active+clean+inconsistent” isso nos mostrar que alguma replicar dentro do cluster está inconsistente.

A passagem do Scrubbing é penosa para o cluster e muitas vezes ele só passará quando o sistema estiver com uma carga menor ou se as configurações forem alteradas via inject nas “OSDs”.

**Verificando configurações no Ceph:**

Apresenta apenas as configurações default do ceph

    # ceph --show-config | grep osd_scrub_load_threshold

Apresenta a configuração permanente do ceph.conf    
        
    # ceph -n osd.X --show-config | grep osd_scrub_load_threshold


Apresentar a configuração atual
        
    # ceph --admin-daemon /var/run/ceph/ceph-osd.21.asok config show | grep osd_scrub_load_threshold


Alterando Configuração a quente

    # ceph tell osd.X injectargs '--osd_scrub_load_threshold 0.5' 


O Scrub é muito importante para manter a integridade dos dados, mas poderá reduzir o desempenho do seu cluster se não for realizado ajustes nas configurações.

Existe dois tipos de Scrub, um e o “Light scrubbing” verifica o tamanho e os atributos do objeto e passa todos os dias e não sobrecarrega tanto seu cluster. O “deep-scrubbing”  e uma limpeza mais profunda  lê os dados e usa somas de verificação para garantir a integridade, ele que passa no decorrer da semana e gera uma carga maior no cluster. Como o “Ceph -s“ conseguimos verificar em quantas “PGs” está executando scrubbing no momento.

> 26 active+clean+scrubbing+deep
> 7 active+clean+scrubbing

Executando o comando abaixo, você consegue ver quanto tempo passou o último scrub/deep-scrub na pg


    # Ceph osd PG_ID query 
    ..................
                "last_deep_scrub_stamp": "2018-08-23 15:48:42.107928",
    ..................   


Algumas configurações que devemos nos atentar:

- osd_scrub_min_interval
- osd_scrub_max_interval
- osd_scrub_load_threshold
- osd_max_scrubs
- osd_deep_scrub_interval
- osd_scrub_interval_randomize_ratio
- osd_scrub_during_recovery

Os Scrubs começam após osd_scrub_min_interval desde o último scrub ter passado, isso só ocorre se a CPU estiver abaixo do osd_scrub_load_threshold ou após osd_scrub_max_interval mesmo se o sistema estiver sobrecarregado.

Podemos também configurar um intervalo na madrugada para o scrub passar osd_scrub_begin_hour/osd_scrub_end_hour, com lançamento do Mimic temos mais duas opções de intervalos osd_scrub_begin_week_day/osd_scrub_end_week_day

Quando executamos um ceph pg repair, ou um ceph pg deep-scrub ele não irá executar imediatamente e sim enviará um pedido a pg e o osd primario “instructing pg ID on osd.X to repair” porem precisa satisfazer as regras configuradas.

> Nota: “Ceph will not scrub when the system load (as defined by getloadavg() / number of onlinecpus) is higher than this number. Default is 0.5.”

A passagem deep-scrub não necessariamente depende do load_threshold

>Nota: “The interval for “deep” scrubbing (fully reading all data). The osd scrub load threshold does not affect this setting.”

Atenção as frags noscrub e nodeep-scrub definida no cluster e nas pools, caso esteja setada o scrub não será executado.

Referencia: http://docs.ceph.com/docs/master/rados/configuration/osd-config-ref/