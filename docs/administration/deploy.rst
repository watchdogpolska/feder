.. _deploy:

***************************************
Uruchomienie w środowisku deweloperskim
***************************************

Został opracowany playbook Ansible, który zapewnia wdrożenie aplikacji. Przedstawia on także podstawowe kroki, które są konieczne do uruchomienia aplikacji. Dostępny jest on w pliku ``vagrant_provision_ansible.yaml``. Zalecane jest wykorzystanie przedstawionego playbooka wraz z środowiskiem wirtualizacyjnym Vagrant. Wówczas konfiguracja całego środowiska to::

    $ vagrant up --provision
    $ vagrant ssh
    vagrant@vagrant:/vagrant$ python manage.py runserver 0.0.0.0:8000

Następnie można przejśc w przeglądarce pod adres ``http://localhost:8000``.

Po zakończeniu pracy można wykonać w celu skasowania wirtualnej maszyny::

    $ vagrant destroy

Alternatywnie w celu zaoszczędzenia pamięci RAM można ją wyłącznie uśpić::

    $ vagrant suspend

Warto także zwrócić uwagę na polecenie zapewniające utworzenie użytkownika administracyjnego::

    vagrant@vagrant:/vagrant$ python manage.py createsuperuser

Jeżeli zepsujesz sobie bazę danych wykonaj::

    vagrant@vagrant:/vagrant$ sudo -H mysql 'drop database feder';
    $ vagrant provision

Jeżeli chcesz skonfigurować maszynę od nowa wykonaj::

    $ vagrant destroy -f && vagrant up --provision

Jeżeli chcesz upewnić się co do aktualności konfiguracji możesz wykonać::

    $ vagrant provision
