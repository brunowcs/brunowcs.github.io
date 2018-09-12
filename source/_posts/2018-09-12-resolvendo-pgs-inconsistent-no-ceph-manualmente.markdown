---
layout: post
title: "Resolvendo PGs inconsistent no CEPH manualmente"
date: 2018-09-12 15:23:02 -0300
comments: true
categories: ceph linux 
---

<span style="display:block;text-align:center">![](/images/ceph/ceph.png) </span>

Recentemente eu tiver um problema de badblock em um dos discos que gerou uma inconsistent na PG e o cluster não conseguiu se resolver automaticamente, mesmo tirando o disco defeituoso do cluster e parando a OSD associada.

As soluções abaixo me ajudaram a resolver meu problema que se estendeu por alguns dias. Caso tenha suporte recomendo abrir um chamado ou faça por sua conta e risco. 

A solução 1 resolver a maioria dos casos e no meu caso não houver impacto nem downtime.

Problema ocorreu no Ubuntu 16.4 com Jewel utilizando FileStore replica de 3.

Antes de iniciar recomendo a leitura do meu post ["Ceph Scrubbing"](http://brunocarvalho.net/blog/2018/09/11/ceph-scrubbing/) será fundamental você entender esse cara antes de começar.


1 - Buscando pgs inconsistente no nosso caso "5.163"


    # ceph health detail  | grep inconsistent
    HEALTH_ERR 
    pg 5.163 is active+remapped+inconsistent+wait_backfill, acting [26,45,135]


> Podemos ver que apresentou também em quais OSDs estão essas pgs [26,45,135] execute o comando abaixo para descobrir em quais servidores estão as OSDs

    root@serv-117:/home/bruno.carvalho# ceph osd find 26
    {   
        "osd": 16,
        "ip": "10.0.0.14:6842\/21992",
        "crush_location": {
            "host": "stor-121",
            "rack": "sata",
            "root": "default"
        }
    }
	root@serv-117:/home/bruno.carvalho# ceph osd find 45
	{
		"osd": 91,
		"ip": "10.0.0.15:6814\/8362",
		"crush_location": {
			"host": "stor-122",
			"rack": "sata",
			"root": "default"
		}
	}
	root@serv-117:/home/bruno.carvalho# ceph osd find 135
	{
		"osd": 30,
		"ip": "10.0.0.17:6812\/10485",
		"crush_location": {
			"host": "stor-124",
			"rack": "sata",
			"root": "default"
		}
	}


2 - Logue no servidor da OSD primaria e busque o objeto problemático, se objeto problemático estiver na primaria não esqueça de descer com primary-affinity.()

    # grep -Hn 'ERR' /var/log/ceph/ceph-osd.26.log (apresentar uma tripa de erro, o importante será o nome do objeto )
	..... log [ERR] : 5.163 .... 
	udata.3b2ab5c0fdd3f.00000000000059d2__head_892078F9__4
	.....

No Monitor podemos buscar com o comando abaixo (apresenta um json grande, porem o importante é o nome do objeto, algo parecido com nome do comando acima.)

    # rados list-inconsistent-obj 5.163--format=json-pretty

Se nescessário jogue a OSD primário para outra OSD.

	# ceph osd primary-affinity 26 0

3 - Logue nos servidores das 3 OSDs, busque o arquivo e verifique o md5 do objeto, seu tamanho e identifique o que está diferente entre os 3, no caso o objeto diferente será o que você irar remover para mandar o cluster se recuperar.

    # find /var/lib/ceph/osd/ceph-26/current/5.163_head/ -name '*00000000000059d2*' -ls
    ...
    /var/lib/ceph/osd/ceph-26/current/5.163_head/rbd\\udata.3b2ab5c0fdd3f.00000000000059d2__head_892078F9__4
    # md5sum /var/lib/ceph/osd/ceph-26/current/5.163_head/rbd\\udata.3b2ab5c0fdd3f.00000000000059d2__head_892078F9__4\
    d12a1f042f2a98a79943c990d3a5b2c8  /var/lib/ceph/osd/ceph-26/current/5.163_head/rbd\\udata.3b2ab5c0fdd3f.00000000000059d2__head_892078F9__4

4 - Set noout no cluster

    # ceph osd set noout

5 - Pare a OSD 

    # systemctl stop ceph-osd@26

6 - Execute o flush do journal

    # ceph-osd -i 26 --flush-journal
    SG_IO: bad/missing sense data, sb[]:  70 00 05 00 00 00 00 0a 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    SG_IO: bad/missing sense data, sb[]:  70 00 05 00 00 00 00 0a 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    2018-08-23 18:31:57.691076 7f69269888c0 -1 flushed journal /var/lib/ceph/osd/ceph-26/journal for object store /var/lib/ceph/osd/ceph-26

7 - Remova o Objecto com problema

    # rm  -rf /var/lib/ceph/osd/ceph-26/current/5.163_head/rbd\\udata.3b2ab5c0fdd3f.00000000000059d2__head_892078F9__4

8 - Corrigindo permissão da OSD

    # chown ceph:ceph -R /var/lib/ceph/osd/ceph-26/current/omap/

9 - Subindo OSD

    # systemctl start ceph-osd@26

10 - Tira o noout no cluster e aguarde o cluster ficar com apenas a pg inconsistent

    # ceph osd unset noout

11 - Vamos agora executar um repair para corrigir o problema.  

    # ceph pg repair 5.163
    
> Agora veja o log da OSD primaria.

	# tail -f /var/log/ceph/ceph-osd.26.log

    2018-08-23 18:33:30.568207 7fc1ee195700 -1 log_channel(cluster) log [ERR] : 5.163 shard 26 missing 5:9f1e0491:::rbd_data.3b2ab5c0fdd3f.00000000000059d2:head
    2018-08-23 18:33:30.568212 7fc1ee195700  0 log_channel(cluster) do_log log to syslog
    2018-08-23 18:33:36.274075 7fc1ee195700 -1 log_channel(cluster) log [ERR] : 5.163 repair 1 missing, 0 inconsistent objects
    2018-08-23 18:33:36.274079 7fc1ee195700  0 log_channel(cluster) do_log log to syslog    
    2018-08-23 18:33:36.274142 7fc1ee195700 -1 log_channel(cluster) log [ERR] : 5.163 repair 1 errors, 1 fixed
    2018-08-23 18:33:36.274144 7fc1ee195700  0 log_channel(cluster) do_log log to syslog

No log acima podemos ver "log [ERR] : 5.163 repair 1 errors, 1 fixed" isso mostra que ele encontrou o objecto que faltava e corrigiu criando novamente a replica.

## Solução 2 ##

 Identificar e remover o objeto problemático na OSD excluindo com ceph-object-tools executando com deep-scrub

Com o objeto problemático já identificado, execute os procedimentos: 4, 5 e 6 após sigar os procedimentos abaixo

1 - Com a OSD down localize o objeto

    # ceph-objectstore-tool --data-path /var/lib/ceph/osd/ceph-26 --journal /var/lib/ceph/osd/ceph-26/journal --pgid 5.163 --op list | grep rbd_data.3b2ab5c0fdd3f.00000000000059d2
    ["5.163",{"oid":"rbd_data.3b2ab5c0fdd3f.00000000000059d2","key":"","snapid":-2,"hash":3828189539,"max":0,"pool":5,"namespace":"","max":0}]

2 - Removendo Objeto.

    # ceph-objectstore-tool --data-path /var/lib/ceph/osd/ceph-26 --journal /var/lib/ceph/osd/ceph-26/journal --pgid 5.163 '{"oid":"rbd_data.3b2ab5c0fdd3f.00000000000059d","key":"","snapid":-2,"hash":3828189539,"max":0,"pool":5,"namespace":"","max":0}' remove
    remove #5:c691b427:::rbd_data.3b2ab5c0fdd3f.00000000000059d2:head#

3 - Corrigir permissão

    # chown -R ceph:ceph /var/lib/ceph/osd/ceph-135/current/omap/

4 - Iniciar OSD

    # systemctl start ceph-osd@26

5 - Execute o deep-scrub na pg (Veja artigo do "Ceph Scrubbing", para execução com espaço de tempo menor)

    # ceph pg deep-scrub 5.163

O deep-scrub no CEPH é um processo que passa em todas OSDs para verificar inconsitencia dos dados e corrigir eventuais problemas,  podemos comparar ao fsck. Dependendo das configurações do seu Cluster o deep-scrub não executará imediatamente, verifique no log da OSD primaria ou execute o seguinte comando query pg e veja data da ultima vez que ele passou.

Se o deep-scrub não for executado, verifique as configurações de osd_scrub_max_interval, também é importante verificar o osd_scrub_load_threshold, pois se sua CPU estiver e um certo limite o deep-scrub não rodará. 

Leia mais sobre: ["Ceph Scrubbing"](http://brunocarvalho.net/blog/2018/09/11/ceph-scrubbing/)


6 - Query pg

    #  ceph pg 5.163 query 
    ..................
            "last_deep_scrub_stamp": "2018-08-23 15:48:42.107928",
    ..................   
    
Também podemos verificar logo no final do comando query o deep-scrub sendo executado na PG.

    "scrub": {
                "scrubber.epoch_start": "57000",
                "scrubber.active": 1,
                "scrubber.state": "WAIT_REPLICAS",
                "scrubber.start": "5:578cfc17:::rbd_data.57e3dd6b7d297f.000000000000b063:0",
                "scrubber.end": "5:578cff8c:::rbd_data.552a0c53cb890c.00000000000046aa:0",
                "scrubber.subset_last_update": "58460'37642760",
                "scrubber.deep": true,
                "scrubber.seed": 4294967295,
                "scrubber.waiting_on": 1,
                "scrubber.waiting_on_whom": [
                    "48"

Após o termino do deep-scrub provavelmente sua pg já estará OK.

Nos próximos posts irei apresentar: 

- **Monitoramento avançado no Ceph** - Falarei sobre Telegraf/Influx/Grafana um dashboard pronto com metricas avançadas de latency/journal/queue/iops/throughput que te ajudaram a ajustar melhor as configurações do seu cluster)
- **Melhores práticas com Ceph** - Desde o Hardware, S.O e configurações do ceph.conf para você obter melhor performance do seu cluster.

Referencia: http://lists.ceph.com/pipermail/ceph-users-ceph.com/