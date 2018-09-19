---
layout: post
title: "Métricas de Latência no CEPH"
date: 2018-09-18 16:42:11 -0300
comments: true
categories: ceph influxdb grafana telegraf
---

<span style="display:block;text-align:center">![](/images/ceph/ceph-metrica-logo.png)</span>

Neste post compartilharei um dashboard em grafana com métricas de latência criado para telegraf com influxdb, visto que pesquisando na internet não achei nada sobre latência para este plugin e não era à toa, pois só na versão Lumiuous foi possível corrigir "admin socket permission" então resolvi criar um do zero e compartilhando com a comunidade, explicando como utilizar tanto no jewel quanto no luminous. 

>Não irei abordar instalação do influxdb, grafana e telegraf pois tem muita coisa na internet, apenas os pontos principais para o dashboard funcionar.

Com o comando abaixo é possível verificar media  latência do commit e apply do Ceph

    # ceph osd perf

    commit_latency(ms) apply_latency(ms)
    ............... ......................

Comentarei os 3 mais importantes:

A gravação do objeto em um cluster com replica de 3 gastará 6 IOs para se concluido por conta da gravação  journal(O_DIRECT) e do disco efetivamente. Na maioria das vezes veremos mais IOPS de write por conta das suboperações do ceph de replicação, diferente do read que só faz leitura na OSD primaria. 

- **ops** - Operações por segundo nas OSDs.
- **Journal_latency** - Tempo que leva para gravar no journal, ou seja, tempo de ack do write para o cliente.(O_DIRECT e O_DSYNC)
- **apply_latency** - Tempo de latência até a transação termina, ou seja, o tempo de gravação + journal.
- **commit_latency** - Tempo que leva para realizar o syncfs() após a expiração do filestore_max_sync_interval, no caso a descida do journal para o disco.
  

As métricas acima são as que nos dão uma media de como anda a latência do nosso cluster, o dashboard abaixo irá apresentar no grafana essas informações entre outras.

Por padrão algumas métricas de subsystem do cluster Ceph já vem ativo, outras temos que ativar no ceph.conf ou via OSDs com inject. Verifique se seu cluster está com os perfs true.

    # ceph --admin-daemon /var/run/ceph/ceph-osd.26.asok  config show | grep perf
    "debug_perfcounter": "0\/0",
    "perf": "true",
    "mutex_perf_counter": "true",
    "throttler_perf_counter": "true",


Crie o arquivo abaixo e não esqueça de adicionar as tags para facilitar a seleção no grafana entre SATA e SSD ou escolha uma tag de sua preferência. 

```bash
# cat /etc/telegraf/telegraf.d/ceph.conf
[[inputs.ceph]]
  ## This is the recommended interval to poll.  Too frequent and you will lose
  ## data points due to timeouts during rebalancing and recovery
  interval = '1m'
  tags = "storage,osd,ssd"
  ## All configuration values are optional, defaults are shown below

  ## location of ceph binary
  ceph_binary = "/usr/bin/ceph"

  ## directory in which to look for socket files
  socket_dir = "/var/run/ceph"

  ## prefix of MON and OSD socket files, used to determine socket type
  #mon_prefix = "ceph-mon"
  osd_prefix = "ceph-osd"

  ## suffix used to identify socket files
  socket_suffix = "asok"

  ## Ceph user to authenticate as, ceph will search for the corresponding keyring
  ## e.g. client.admin.keyring in /etc/ceph, or the explicit path defined in the
  ## client section of ceph.conf for example:
  ##
  ##     [client.telegraf]
  ##         keyring = /etc/ceph/client.telegraf.keyring
  ##
  ## Consult the ceph documentation for more detail on keyring generation.
  #ceph_user = "client.telegraf"

  ## Ceph configuration to use to locate the cluster
  #ceph_config = "/etc/ceph/ceph.conf"

  ## Whether to gather statistics via the admin socket
  gather_admin_socket_stats = true

  ## Whether to gather statistics via ceph commands, requires ceph_user and ceph_config
  ## to be specified
  #gather_cluster_stats = true

```

Será nescessario adicionar o usuario telegraf no grupo ceph para que ele possa ler os sockets do /var/run/ceph 

    # addgroup telegraf ceph

**ATENÇÃO:** Aqui está o pulo do gato, nas versões anteriores ao Ceph 12.0.3 Luminous, terá que executar o seguinte comando abaixo

    # chmod  g+w /var/run/ceph/*

Esse comando contorna o problema "admin socket permission" que foi corrigido nas versões acima da 12.0.3

>common: common/admin_socket: add config for admin socket permission bits (pr#11684, runsisi)
>https://github.com/ceph/ceph/pull/11684

Se a OSD for reiniciada a permissão se perder, se estiver abaixo da 12.0.3, recomendo adicionar a permissão no systemd após o startup da OSD. Se já estiver na versão superior basta adicionar no ceph.conf a config abaixo

    admin_socket_mode 0775

Reiniciei o telegraf

    systemctl restart telegraf 

Verifique se não está ocorrendo nenhum error de socket no syslog

    telegraf[986875]: 2018-09-18T21:49:03Z E! error reading from socket '/var/run/ceph/ceph-osd.51.asok': error running ceph dump: exit status 22

Teste se o telegraf está coletando as metricas do seu servidor de OSD com a permissão do telegraf

    # sudo -u telegraf telegraf --debug -test -config /etc/telegraf/telegraf.conf -config-directory /etc/telegraf/telegraf.d  -input-filter ceph

    # sudo -u telegraf ceph --admin-daemon /var/run/ceph/ceph-osd.14.asok perf dump

Se tudo estiver ok, basta importa o dashboard para seu grafana e ser feliz! :)


Dashboard Telegraf Ceph - Latency: https://grafana.com/dashboards/7995

Plugin Utilizado: https://github.com/influxdata/telegraf/tree/master/plugins/inputs/ceph


<span style="display:block;text-align:center">![](/images/ceph/ceph-latencia.PNG) </span>
<span style="display:block;text-align:center">![](/images/ceph/ceph-grafico.PNG) </span>

Referências de métricas: 

https://access.redhat.com/documentation/en-us/red_hat_ceph_storage/3/html/administration_guide/performance_counters

