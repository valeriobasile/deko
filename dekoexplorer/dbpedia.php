<?php
require_once('render.php');
/* ARC2 static class inclusion */
require_once('semsol/ARC2.php');

function get_dbpedia_image_url($resource_url) {
/*    $dbpconfig = array(
    "remote_store_endpoint" => "https://dbpedia.org/sparql",
     );

    $store = ARC2::getRemoteStore($dbpconfig);

    if ($errs = $store->getErrors()) {
       echo "<h1>getRemoteSotre error<h1>" ;
    }

    $query = '
    select distinct ?img where {
    <'.$resource_url.'> <http://dbpedia.org/ontology/thumbnail> ?img .
    }';

    $rows = $store->query($query, 'rows');

    if ($errs = $store->getErrors()) {
        echo "Query errors" ;
        print_r($errs);
    }

    if (count($rows) > 0) {
        return $rows[0];
    }
    else {
        return "pics/noimage.jpg";
    }
    */
    $object_label = str_replace ("http://dbpedia.org/resource/", "", $resource_url);
    return "pics/dbpedia/".$object_label.".jpg";
}

function explore_dbpedia_object($resource_url) {
    global $object_label;

    $imgurl = get_dbpedia_image_url($resource_url);
    print ("<div id=\"title\">");
    print ("<h1>".$object_label."</h1>");
    print ("<span id=\"uri\"><a href=\"".$resource_url."\">".$resource_url."</a><br/>");
    if (is_file($imgurl)) {
        print ("<a href=\"".$imgurl."\"><img id=\"image\" src=\"".$imgurl."\" /></a>");
    }
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
        print "A <strong>".$object_label."</strong> is:";
        print "<ul>";
        foreach( $rows as $row ) {
            print "<li>";
            render_graph($row['src']);
            render_property($row['p']);
            print " ";
            render_resource($row['o']);
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
            render_property($row['p']);
            print " ";
            render_resource($resource_url);
            print "</li>";
        }
        echo "</ul>";
        echo "</div>";
    }

    if (count($rows) == 0) {
        echo $object_url." is not a resource in DeKO";
    }
}
?>
