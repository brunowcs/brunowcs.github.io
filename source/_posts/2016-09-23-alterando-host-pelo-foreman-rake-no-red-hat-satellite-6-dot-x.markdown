---
layout: post
title: "Alterando Host pelo foreman-rake no Red hat Satellite 6.x"
date: 2016-09-23 15:05:16 -0300
comments: true
categories: satellite rhel centos linux
---
Atualmente tive problema com interface invalida ao atualizar provisionamento do host utulizando o dashboard no satellite 6.2.

Este problema ocorre por alguma mudança na interface que foi atualizado pelo factor do satellite e no momento a interface não existe mais e/ou está inconsistente com os dados fornecidos.

Abaixo executo comandos para contorna esse problema, removendo uma interface invalida no host.


    # foreman-rake console
    Loading production environment (Rails 4.1.5)
    
    irb(main):001:0> host = Host.find_by_name('HOSTNAME')
    
    irb(main):003:0> i = host.interfaces[1]
  
    irb(main):004:0> i.destroy
    

Trocando o array "host.interfaces[0,1,2]" você pode navegar em todas interfaces, veja no dashboard ao editar e atualizar o host, quais estão apresentado problemas e remova pelo foreman-rake.

Caso queira editar algum atributo da interface pelo foreman-rake utilize da seguinte forma.
    
    # foreman-rake console
    Loading production environment (Rails 4.1.5)

    irb(main):001:0> host = Host.find_by_name('HOSTNAME')

    irb(main):002:0> i = host.interfaces[0]

    irb(main):003:0> i.name = "hostname"

    irb(main):004:0> i.save!
    
Adpatando os comandos acima pode ser alterar varios atributos do provisionamento pelo foreman-rake.