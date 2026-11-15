#!/usr/bin/env python3
"""Inspect CAF identity and musical metadata without decoding or playback."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

APPLE_INFO_UUID=bytes.fromhex('29819273b5bf4aefb78d62d1ef90bb2c')

def inspect(path):
    path=Path(path)
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    result={'file':str(path),'sha256':digest.hexdigest(),'has_audio_data':False,'has_midi_chunk':False}
    metadata={};valid_frames=None;data_size=None;frames_per_packet=0;bytes_per_packet=0
    size=path.stat().st_size
    with path.open('rb') as f:
        if f.read(8)[:4]!=b'caff':raise ValueError('Expected a CAF file')
        while f.tell()<size:
            header=f.read(12)
            if len(header)!=12:raise ValueError('Truncated CAF chunk header')
            kind=header[:4];length=struct.unpack('>q',header[4:])[0]
            if length<0 or length>size-f.tell():raise ValueError('Unknown-size or truncated CAF chunk')
            start=f.tell()
            if kind==b'desc':
                if length<32:raise ValueError('Truncated CAF audio description')
                data=f.read(32)
                sample_rate,codec,flags,bytes_per_packet,frames_per_packet,channels,bits=struct.unpack('>d4sIIIII',data)
                result.update(sample_rate=sample_rate,channels=channels,codec=codec.decode('ascii',errors='replace'))
            elif kind==b'pakt':
                if length<24:raise ValueError('Truncated CAF packet table')
                data=f.read(24);valid_frames=struct.unpack_from('>q',data,8)[0]
            elif kind==b'data':result['has_audio_data']=length>4;data_size=length-4
            elif kind.lower()==b'midi':result['has_midi_chunk']=True
            elif kind==b'uuid' and length>=20:
                prefix=f.read(20)
                if prefix[:16]==APPLE_INFO_UUID:
                    if length>1024*1024:raise ValueError('Unexpectedly large Apple metadata chunk')
                    pairs=f.read(length-20).decode('utf-8').rstrip('\0').split('\0')
                    count=struct.unpack_from('>I',prefix,16)[0]
                    if len(pairs)!=count*2:raise ValueError('Malformed Apple metadata pairs')
                    metadata.update(zip(pairs[::2],pairs[1::2]))
            f.seek(start+length)
    result['metadata']=metadata
    if valid_frames is None and result.get('codec')=='lpcm' and bytes_per_packet:
        valid_frames=(data_size or 0)//bytes_per_packet*frames_per_packet
    if valid_frames is not None and result.get('sample_rate',0)>0:
        duration=valid_frames/result['sample_rate'];result['duration_seconds']=duration
        if 'beat count' in metadata:
            beats=int(metadata['beat count']);result['beat_count']=beats
            if duration>0:result['tempo_bpm']=beats*60/duration
    channels=result.get('channels')
    result['stereo_source']=channels==2
    result['audio_only_candidate']=bool(result['has_audio_data'] and not result['has_midi_chunk'] and channels in (1,2))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('files',nargs='+',type=Path);a=p.parse_args()
    print(json.dumps([inspect(x) for x in a.files],indent=2))
if __name__=='__main__':main()
