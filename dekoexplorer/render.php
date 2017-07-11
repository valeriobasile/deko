<?php

$graph_colors = array("KeywordLinking" => "#f0f0a0",
    "DistributionalRelationalHypothesis" => "#f0a0a0",
    "KNEWS" => "#f0a0f0",
    "Crowdsourcing" => "#a0f0a0");

function render_property($property) {
    if ($property == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type") {
        print ('of type');
    }
    elseif (strpos($property, '#') !== false) {
        $label = end(explode('#', $property));
        print "<a href='".$property."'>".$label."</a>";
    }
    else {
        $label = end(explode('/', $property));
        print "<a href='".$property."'>".$label."</a>";
    }

}

function render_resource($resource) {
    if (strpos($resource, '#') !== false) {
        $label = end(explode('#', $resource));
    }
    else {
        $label = end(explode('/', $resource));
    }
    print "<a href='index.php?url=".$resource."'>".$label."</a> ";
}

function render_graph($graph) {
    global $graph_colors;
    $graph_label = end(explode('#', $graph));
    $color = $graph_colors[$graph_label];
    print "<span style='background-color: ".$color."; width:2em;'>&nbsp;</span> ";
}

function legend() {
    global $graph_colors;
    print "<div id=\"legend\">Graph:<br/>";
    foreach ($graph_colors as $graph_name => $graph_color) {
        print ("<span style='background-color: ".$graph_color."; width:2em;'>&nbsp;&nbsp;&nbsp;</span> ". $graph_name." ");
    }
    print ("</div>");
}
?>
