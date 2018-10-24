import nilearn
from nilearn import image
from nilearn.input_data import NiftiMasker
import nibabel as nb
import os
import numpy as np
import rena
import matplotlib.pyplot as plt
import glob

# Befor run edit the dir_name to the path of your subject; include / at the end
dir_name = "MRI_ReNA/study_dir/"
f_len = len(dir_name.split('/'))
f_len = f_len - 2

'''mask_img = nb.load('MRI_ReNA/study_dir/TBI_INVAX364NTZ/T1.nii.gz')
nifti_masker = NiftiMasker(mask_img=mask_img, smoothing_fwhm=False,
                           standardize=False)
nifti_masker.fit()'''

# using subject TBI_INVDD132CG0 FLAIR as masker for all data
nifti_masker = NiftiMasker(smoothing_fwhm=False,
                           standardize=False)
nifti_masker.fit('MRI_ReNA/study_dir/TBI_INVDD132CG0/FLAIR.nii.gz')

'''
mask_img = nb.load('../../../stochastic_regularizer/sergul_aydore/supporting_data/grey10_icbm_2mm_bin.nii.gz')
nifti_masker = NiftiMasker(mask_img=mask_img, smoothing_fwhm=False,
                           standardize=False)
nifti_masker.fit()'''


def subject_checker(study_folder):
    subject_list = glob.glob(study_folder + 'TBI*')
    target_subject = []

    for subject in subject_list:

        t1file = os.path.join(subject, 'T1.nii.gz')
        t2file = os.path.join(subject, 'T2.nii.gz')
        fl = os.path.join(subject, 'FLAIR.nii.gz')

        if not (os.path.isfile(t1file) and os.path.isfile(t2file)
                and os.path.isfile(fl)):
            print("one file missing (T1,T2 or FLAIR), go to the next subject\n")
            continue
        else:
            target_subject.append(subject)

    return target_subject


def get_single_subject(file_name):
    t1file = os.path.join(file_name, 'T1.nii.gz')
    t2file = os.path.join(file_name, 'T2.nii.gz')
    fl = os.path.join(file_name, 'FLAIR.nii.gz')

    t1 = nifti_masker.transform(image.load_img(t1file))
    t2 = nifti_masker.transform(image.load_img(t2file))
    flair = nifti_masker.transform(image.load_img(fl))

    p = np.percentile(np.ravel(t1), 95)  # normalize to 95 percentile
    t1 = np.float32(t1) / p

    p = np.percentile(np.ravel(t2), 95)  # normalize to 95 percentile
    t2 = np.float32(t2) / p

    p = np.percentile(np.ravel(flair), 95)  # normalize to 95 percentile
    flair = np.float32(flair) / p

    imgs = np.concatenate((t1, t2, flair))

    return imgs


all_imgs = None

# checker include only the subject with T1,T2 and FLAIR MRI data
subject_list = subject_checker(dir_name)
# print(subject_list) # just to chekc we have the right subject
print(subject_list)
for subject_name in subject_list:

    file_name = subject_name
    imgs = get_single_subject(file_name)

    if all_imgs is None:
        all_imgs = imgs
    else:
        all_imgs = np.concatenate((all_imgs, imgs))

print('all images concatenate shape is ', all_imgs.shape, '\n')

n_voxels = all_imgs.shape[1]
n_samples = all_imgs.shape[0]
n_clusters = int(20 * n_voxels / 100)
cluster = rena.ReNA(scaling=True,
                    n_clusters=n_clusters,
                    masker=nifti_masker)

print(' no. of voxels: ', n_voxels, '\n',
      'no. of samples: ', n_samples, '\n',
      'no. of clusters: ', n_clusters, '\n\n')

cluster.fit(all_imgs)

reduced_images = cluster.transform(all_imgs)
reconstructed_images = cluster.inverse_transform(reduced_images)

mse = np.mean(abs(all_imgs - reconstructed_images) ** 2, axis=1)

labels_plot = []
for labels_p in subject_list:
    c_list = glob.glob(labels_p + '/*')
    # if there are other type nii.gz not wanted included as shown with 'fse.nii.gz'
    # ../../sample_data/TBI*/*  >>> 0/1/2/3/4
    # use f_len here
    for c in c_list:
        if c.split('/')[f_len + 2][0:2] == 'T1':
            labels_plot.append(c.split('/')[f_len + 1] + '-' + c.split('/')[f_len + 2][0:2])
    for c in c_list:
        if c.split('/')[f_len + 2][0:2] == 'T2':
            labels_plot.append(c.split('/')[f_len + 1] + '-' + c.split('/')[f_len + 2][0:2])
    for c in c_list:
        if c.split('/')[f_len + 2][0:2] == 'FL':
            labels_plot.append(c.split('/')[f_len + 1] + '-' + c.split('/')[f_len + 2][0:2])

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(mse, marker='o')
ax.set_xticks(range(n_samples))
ax.set_xticklabels(labels_plot, rotation=70)
ax.set_ylabel("MSE")
plt.tight_layout()
plt.show()
