<?php
require_once('render.php');
/* ARC2 static class inclusion */
require_once('semsol/ARC2.php');

function explore_babelnet_object($resource_url) {
    global $object_label;

    $service_url = 'https://babelnet.io/v4/getSynset';

    $id = str_replace('s', 'bn:', $object_label);
    $key  = 'YOUR_KEY_HERE';

    $params = array(
      'id'    => $id,
      'key'   => $key
    );

    $url = $service_url . '?' . http_build_query($params);

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_ENCODING, 'gzip');
    $response = json_decode(curl_exec($ch), true);
    curl_close($ch);

    # retrieving BabelSense data
    $lemmas = array();
    foreach($response['senses'] as $result) {
      $language = $result['language'];
      if ($language == 'EN') {
          array_push($lemmas, $result['lemma']);
      }
    }

    # retrieving BabelImage data
    foreach($response['images'] as $result) {
      $language = $result['language'];
      //if ($language == 'EN') {
          $imgurl = $result['url'];
          break;
      //}
    }

    # retrieving BabelGloss data
    foreach($response['glosses'] as $result) {
      $language = $result['language'];
      if ($language == 'EN') {
          $gloss = $result['gloss'];
          break;
      }
    }

    if (count($lemmas) > 1) {
        $object_label = $lemmas[0];
    }

    print ("<div id=\"title\">");
    print ("<h1>".$object_label."</h1>");
    print ("<span id=\"lemma\">".implode(array_slice($lemmas, 0, 5), ', ')."</span><br/>");
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
}
?>
