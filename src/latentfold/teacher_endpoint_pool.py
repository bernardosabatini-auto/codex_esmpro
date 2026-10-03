"""Independent endpoint draws; never alter conditioning or primary RNG streams."""
import h5py,numpy as np,torch


class TeacherEndpointPool:
    def __init__(self,path,seed):
        self.rng=np.random.default_rng(seed);self.states={};self.eligible={}
        with h5py.File(path) as f:
            for ident,g in f.items():
                if 'teacher_z' in g:self.states[ident]=torch.from_numpy(g['teacher_z'][:])
                for name,q in g['retained'].items():self.eligible[ident,name]=q[:].tolist()

    def draw(self,ids,conditions,reference):
        if reference.device.type!='cpu' or len(ids)!=len(reference) or len(conditions)!=len(ids):raise ValueError('Matching CPU target batch required')
        draws=self.rng.random((len(ids),2));target=reference.clone();selected=[]
        for row,(ident,condition) in enumerate(zip(ids,conditions)):
            choices=self.eligible[ident,condition];index=-1
            if choices and draws[row,0]<.5:
                index=choices[int(draws[row,1]*len(choices))];z=self.states[ident][index]
                if z.shape[-1]!=8 or len(z)>target.shape[1] or not torch.isfinite(z).all():raise ValueError('Invalid teacher endpoint')
                target[row,:len(z)]=z
            selected.append(index)
        return target,selected
