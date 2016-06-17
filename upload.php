<?

$id = $argv[1];
$file = $argv[2];
$course = $argv[3];



if( !file_exists( $file ) ) {
    die();
}

$curlFile = new CURLFile( $argv[2] );
$curlFile->setPostFilename( basename( $argv[2] ) );
$curlFile->setMimeType( "audio/mpeg" );

$post = array(
    'thing_id'  => $id,
    'cell_id'   => '4',
    'cell_type' => 'column',
    'csrfmiddlewaretoken'   => '2N828n66bh5Alhbc463wYtoqpyWosyON',
    'f' => $curlFile,
);

$curl = curl_init( "http://www.memrise.com/ajax/thing/cell/upload_file/" );
curl_setopt_array( $curl, array(
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_REFERER => $course,
    CURLOPT_USERAGENT => "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0",
    CURLOPT_COOKIE => "Cookie:__uvt=; __utmt=6; csrftoken=2N828n66bh5Alhbc463wYtoqpyWosyON; sessionid=zj8suxtx841zlwrn10o6x3suzdjw9wpt; __utma=216705802.691983187.1416840006.1429942996.1430039373.8; __utmb=216705802.4.10.1440411307; __utmc=216705802; __utmz=216705802.1416840006.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); uvts=2Mnc8QsWzuuv8GVh",
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $post,
    CURLOPT_TIMEOUT => 60,
) );
$res = curl_exec( $curl );