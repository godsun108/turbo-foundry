#include "earth_studio/c_api.h"
#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
void require(bool ok,const char*m){if(!ok){std::cerr<<"FAIL: "<<m<<'\n';std::exit(1);}}
int main(){
 auto*h=earth_engine_create(48000);require(h!=nullptr,"create");
 earth_instrument_parameters p{0U,.001F,.001F,1.0F,.05F,12000.0F,0.0F,5.0F,0.0F};require(earth_engine_set_instrument(h,&p)==0,"set params");
 std::array<float,256> out{};earth_midi_event on{0U,0U,0U,69U,0U,1.0F};
 require(earth_engine_render(h,out.data(),128U,&on,1U)==0,"render");bool audible=false;for(float x:out)audible|=std::abs(x)>.0001F;
 require(audible,"audio crosses C ABI");require(earth_engine_active_voices(h)==1U,"voice stats");
 earth_midi_event bad{128U,0U,0U,60U,0U,1.0F};require(earth_engine_render(h,out.data(),128U,&bad,1U)==-2,"invalid event rejected");
 require(earth_engine_render(nullptr,out.data(),128U,nullptr,0U)==-1,"null handle rejected");require(earth_engine_render(h,out.data(),2049U,nullptr,0U)==-1,"oversized block rejected");
 earth_engine_destroy(h);std::cout<<"EARTH STUDIO C ABI tests passed\n";
}