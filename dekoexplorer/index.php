<?php
require_once('dbpedia.php');
require_once('babelnet.php');
require_once('frame.php');
require_once('render.php');

$welcome = false;
if (!isset($_GET["url"])) {
    $object_label = "Welcome";
    $welcome      = true;
} else {
    $resource_url = htmlentities($_GET["url"]);
    if (substr($resource_url, 0, 28) == 'http://dbpedia.org/resource/') {
        # DBpedia resource
        $object_type  = 'DBpedia';
        $object_label = str_replace("http://dbpedia.org/resource/", "", $resource_url);
    } elseif (substr($resource_url, 0, 24) == 'http://babelnet.org/rdf/') {
        # BabelNet resource
        $object_type  = 'BabelNet';
        $object_label = str_replace("http://babelnet.org/rdf/", "", $resource_url);
    } elseif (substr($resource_url, 0, 27) == 'http://framebase.org/frame/') {
        # FrameNet frame
        $object_type  = 'Frame';
        $object_label = str_replace("http://framebase.org/frame/", "", $resource_url);
    } elseif (substr($resource_url, 0, 24) == 'http://framebase.org/fe/') {
        # BabelNet resource
        $object_type  = 'Role';
        $object_label = str_replace("http://framebase.org/fe/", "", $resource_url);
    }
}
?>
<!DOCTYPE html>
<html>
  <head>
      <title><?= $object_label ?> - DeKO Explorer</title>
      <link rel="stylesheet" href="deko.css" />
      <link href="https://fonts.googleapis.com/css?family=Work+Sans" rel="stylesheet" />
       <link href="https://fonts.googleapis.com/css?family=Arvo" rel="stylesheet" />
  </head>
  <body>
      <div id="header">
          <a href="http://deko-demo.inria.fr/"><img src="DeKO_logo.png" /></a><br/>
          Default Knowledge about Objects
      </div>
<?php
if ($welcome == true) {
?>
<script language="javascript">
function sendquery() {
    var object = document.getElementById('query').value;
    document.getElementById('url').value="http://dbpedia.org/resource/"+object;
    document.getElementById('search').submit();
}
</script>
Search DeKO:
<form id="search" name="search" action="index.php" method="get">
<input type="text" list="objects" id="query">
<datalist id="objects">
<?php
    $file_lines = file('objects.txt');
    foreach ($file_lines as $line) {
        print("<option>" . $line . "</option>");
    }
?>
</datalist>
<input type="button" value="search" onclick="sendquery();" />
<input type="hidden" id="url" name="url"/>
</form>
<?php
} else {
    if ($object_type == 'DBpedia') {
        explore_dbpedia_object($resource_url);
    } elseif ($object_type == 'BabelNet') {
        explore_babelnet_object($resource_url);
    } elseif ($object_type == 'Frame') {
        explore_frame($resource_url);
    } elseif ($object_type == 'Role') {
        explore_role($resource_url);
    }
    
    legend();
}
?>
  </body>
</html>
