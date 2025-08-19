<?php
namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;

class SynologyFileStation {
  protected string $host; protected string $user; protected string $pass; protected bool $verify;
  public function __construct(){
    $this->host=rtrim(env('SYNOLOGY_HOST'),'/');
    $this->user=env('SYNOLOGY_USER'); $this->pass=env('SYNOLOGY_PASS');
    $this->verify=filter_var(env('SYNOLOGY_VERIFY_SSL',false), FILTER_VALIDATE_BOOL);
  }
  protected function client(){ return Http::withOptions(['verify'=>$this->verify]); }

  protected function login(): string {
    $r=$this->client()->asForm()->post($this->host.'/webapi/auth.cgi',[
      'api'=>'SYNO.API.Auth','version'=>3,'method'=>'login',
      'account'=>$this->user,'passwd'=>$this->pass,'session'=>'FileStation','format'=>'sid',
    ]);
    if(!$r->ok()||!$r->json('success')) throw new \RuntimeException('Login DSM gagal: '.json_encode($r->json()));
    return $r->json('data.sid');
  }

  public function createShareLink(string $absPath, ?string $expireYmd=null, ?string $password=null): ?string {
    $sid=$this->login();
    $pathParam='"'.$this->nasPathForApi($absPath).'"';
    $form=['api'=>'SYNO.FileStation.Sharing','version'=>3,'method'=>'create','path'=>$pathParam,'_sid'=>$sid];
    if($expireYmd){ $form['date_expired']='"'.$expireYmd.'"'; }
    if($password){ $form['password']=$password; }
    $r=$this->client()->asForm()->post($this->host.'/webapi/entry.cgi',$form);
    return ($r->ok() && $r->json('success')) ? ($r->json('data.links.0.url') ?? null) : null;
  }

  protected function nasPathForApi(string $absPath): string {
    $p=str_replace('\\','/',$absPath);
    if(Str::startsWith($p,'/volume')){
      $parts=explode('/',ltrim($p,'/')); array_shift($parts);
      return '/'.implode('/',$parts); // contoh: /DrivePublic/uploads/file.pdf
    }
    return $p;
  }
}