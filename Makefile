export_pgsql:
	sudo docker cp database:/out.pgsql ./out.pgsql

inport_pgsql:
	sudo docker cp ./out.pgsql database:/out.pgsql
	