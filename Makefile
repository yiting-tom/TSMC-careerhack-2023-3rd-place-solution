export_pgsql:
	sudo docker cp database:/out.pgsql ./out.pgsql

import_pgsql:
	sudo docker cp ./out.pgsql database:/out.pgsql
	