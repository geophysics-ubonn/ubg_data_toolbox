#!/usr/bin/env python
import pandas as pd

def main():
    data = pd.read_pickle('.management/db.pickle')
    with open('overview.html', 'w') as fid:
        fid.write('<html>\n')
        fid.write('<head>\n')
        fid.write("""<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
             <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.3/css/jquery.dataTables.css">
            <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.3/js/jquery.dataTables.js"></script>
            <script>
                    $(document).ready( function () { $('#data_table').DataTable(
                    {
                        search: {
                            return: true
                        }
                    }
                    ); } );
            </script>
      </head>
    <body>""")
        fid.write(
            data.to_html(classes=['display', ], table_id='data_table')
        )
        fid.write('</body></html>')

if __name__ == '__main__':
    main()
