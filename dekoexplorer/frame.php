<?php
require_once('render.php');

function explore_frame($resource_url) {
    global $object_label;

    print ("<div id=\"title\">");
    print ("<h1>".$object_label."</h1>");
    print ("<span id=\"uri\"><a href=\"".$resource_url."\">".$resource_url."</a><br/>");
    print ("</div>");

    $dbpconfig = array(
    "remote_store_endpoint" => "http://localhost:3030/deko/sparql",
     );

    $store = ARC2::getRemoteStore($dbpconfig);

    if ($errs = $store->getErrors()) {
       echo "<h1>getRemoteSotre error<h1>" ;
    }

    # direct properties
    $query = '
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix dbr: <http://dbpedia.org/resource/>
    prefix deko: <http://ns.inria.fr/deko/ontology/deko.owl#>

    SELECT ?src ?p ?o
    WHERE
     {
       GRAPH ?src
       { <'.$resource_url.'> ?p ?o
       }
     }';

    /* execute the query */
    $rows = $store->query($query, 'rows');

    if ($errs = $store->getErrors()) {
        echo "Query errors" ;
        print_r($errs);
    }

    /* loop for each returned row */
    if (count($rows) > 0) {
        print "<div class=\"properties\" id=\"direct_properties\">";
        print "The frame <strong>".$object_label."</strong> involves:";
        print "<ul>";
        foreach( $rows as $row ) {
            print "<li>";
            render_graph($row['src']);
            render_resource($row['o']);
            print " as ";
            render_property($row['p']);
            print "</li>";
        }
        echo "</ul>";
        echo "</div>";
    }
    # inverse properties
    $query = '
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix dbr: <http://dbpedia.org/resource/>
    prefix deko: <http://ns.inria.fr/deko/ontology/deko.owl#>

    SELECT ?src ?s ?p
    WHERE
    {
     GRAPH ?src
     { ?s ?p <'.$resource_url.'>
     }
    }';

    /* execute the query */
    $rows = $store->query($query, 'rows');

    if ($errs = $store->getErrors()) {
        echo "Query errors" ;
        print_r($errs);
    }

    /* loop for each returned row */
    if (count($rows) > 0) {
            print "<div class=\"properties\" id=\"inverse_properties\">";
        print "also:";
        print "<ul>";
        foreach( $rows as $row ) {
            print "<li>";
            render_graph($row['src']);
            render_resource($row['s']);
            print " is the ";
            render_property($row['p']);
            print " in the frame ";
            render_resource($resource_url);
            print "</li>";
        }
        echo "</ul>";
        echo "</div>";
    }
}

function explore_role($resource_url) {
    global $object_label;

    print ("<div id=\"title\">");
    print ("<h1>".$object_label."</h1>");
    print ("<span id=\"uri\"><a href=\"".$resource_url."\">".$resource_url."</a><br/>");
    print ("<a href=\"".$imgurl."\"><img id=\"image\" src=\"".$imgurl."\" /></a>");
    print ("<span id=\"gloss\">".$gloss."</span><br/>");
    print ("</div>");

    $dbpconfig = array(
    "remote_store_endpoint" => "http://localhost:3030/deko/sparql",
     );

    $store = ARC2::getRemoteStore($dbpconfig);

    if ($errs = $store->getErrors()) {
       echo "<h1>getRemoteSotre error<h1>" ;
    }

    # direct properties
    $query = '
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix dbr: <http://dbpedia.org/resource/>
    prefix deko: <http://ns.inria.fr/deko/ontology/deko.owl#>

    SELECT ?src ?p ?o
    WHERE
     {
       GRAPH ?src
       { <'.$resource_url.'> ?p ?o
       }
     }';

    /* execute the query */
    $rows = $store->query($query, 'rows');

    if ($errs = $store->getErrors()) {
        echo "Query errors" ;
        print_r($errs);
    }

    /* loop for each returned row */
    if (count($rows) > 0) {
        print "<div class=\"properties\" id=\"direct_properties\">";
        print "The frame <strong>".$object_label."</strong> involves:";
        print "<ul>";
        foreach( $rows as $row ) {
            print "<li>";
            render_graph($row['src']);
            render_resource($row['o']);
            print " as ";
            render_property($row['p']);
            print "</li>";
        }
        echo "</ul>";
        echo "</div>";
    }
    # inverse properties
    $query = '
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix owl: <http://www.w3.org/2002/07/owl#>
    prefix dbr: <http://dbpedia.org/resource/>
    prefix deko: <http://ns.inria.fr/deko/ontology/deko.owl#>

    SELECT ?src ?s ?p
    WHERE
    {
     GRAPH ?src
     { ?s ?p <'.$resource_url.'>
     }
    }';

    /* execute the query */
    $rows = $store->query($query, 'rows');

    if ($errs = $store->getErrors()) {
        echo "Query errors" ;
        print_r($errs);
    }

    /* loop for each returned row */
    if (count($rows) > 0) {
            print "<div class=\"properties\" id=\"inverse_properties\">";
        print "also:";
        print "<ul>";
        foreach( $rows as $row ) {
            print "<li>";
            render_graph($row['src']);
            render_resource($row['s']);
            print " is the ";
            render_property($row['p']);
            print " in the frame ";
            render_resource($resource_url);
            print "</li>";
        }
        echo "</ul>";
        echo "</div>";
    }
}

?>
