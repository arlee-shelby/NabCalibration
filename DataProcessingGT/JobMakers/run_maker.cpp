#include <string>
#include <fstream>
using namespace std;

string scriptBaseName = "energyHistJobRun";
string pixelFileName = "LDETpixelsGT_3.txt";
string runDirectoryName = "/storage/ideas/is-ajezghani3-0/TempCal/";
// string detectorType = "LDET";

void singleJob(int runNumber, string pixels, string detectorType) {
    string scriptName = detectorType + scriptBaseName;
    string JobNamePart = scriptName+to_string(runNumber)+".sh";
    string JobName = "../JobScripts/"+scriptName+to_string(runNumber)+".sh";

    printf("JobName=%s\n", JobName.c_str());
	FILE* fp;
	fp = fopen(JobName.c_str(), "w");
	if (!fp) {
        printf("❌ ERROR: cannot open %s\n", JobName.c_str());
        return;
    }
    printf("✅ Opened JobName\n");

    fprintf(fp,"#!/bin/bash\n");
	fprintf(fp,"\n");
    fprintf(fp,"#SBATCH -A gts-ajezghani3\n");
	fprintf(fp,"#SBATCH --nodes=1\n");
	fprintf(fp,"#SBATCH --ntasks=1\n");
    fprintf(fp,"#SBATCH --mem=80gb\n");
    fprintf(fp,"#SBATCH --cpus-per-task=24\n");
	fprintf(fp,"#SBATCH -t0-20\n");

    string outputFileCommand = "#SBATCH --output=/storage/home/hcoda1/4/ashelby8/NabCalibration/DataPcrocessingGT/SlurmOutput/run"+to_string(runNumber)+"_slurmjob%j"+".out\n";
    fputs(outputFileCommand.c_str(),fp);
	fprintf(fp,"\n");
    fprintf(fp,"source /storage/home/hcoda1/4/ashelby8/Manitoba/bin/activate\n");
    fprintf(fp,"cd /storage/home/hcoda1/4/ashelby8/NabCalibration/DataProcessingGT/nabPyDataProcessing\n");
    fprintf(fp,"\n");

    string RunCommand = "srun python -u get_pixels_hist_df.py -dt "  + detectorType + " -d " + runDirectoryName + " -r " + to_string(runNumber) + " -p " + pixels +"\n";
    fprintf(fp,"%s",RunCommand.c_str());
    fclose(fp);

    fp = fopen("../JobScripts/SubmitManyJobs.sh", "a");
    if (!fp) { printf("❌ Failed to open ../JobScripts/SubmitManyJobsGT.sh\n"); return; }
	printf("✅ Opened ../SubmitManyJobsGT.sh\n");
    fprintf(fp,"chmod +x ./%s\n",JobNamePart.c_str());
	fprintf(fp,"sbatch ./%s\n",JobNamePart.c_str());
	fprintf(fp,"\n");
	fclose(fp);
}

void Looper(string detectorType) {
    const int nRuns = 104;
    int runNumbers[nRuns] = {8657, 8645, 8643, 8637, 8636, 
    8635, 8644, 8656, 8655, 8654, 
    8653, 8652, 8651, 8658, 8625, 
    8624, 8623, 8622, 8626, 8627, 
    8659, 8646, 8647, 8648, 8649, 
    8650, 8631, 8630, 8629, 8628, 
    8632, 8699, 8698, 8696, 8694,
    8693, 8692, 8697, 8684, 8683,
    8682, 8681, 8685, 8686, 8690, 
    8689, 8688, 8687, 8691,8717, 
    8710, 8709, 8708, 8707, 8706, 
    8705, 8720, 8711, 8721, 8712, 
    8713, 8715, 8716, 8704, 8719, 
    8718, 8824, 8825, 8826, 8827, 
    8828, 8829, 8830, 8831, 8832, 
    8834, 8835, 8837, 8838, 8839, 
    8840, 8841, 8842, 8843, 8844, 
    8845, 8846, 8847, 8848, 8849, 
    8850, 8853, 8854, 8855, 8856, 
    8857, 8858, 8859, 8860, 8861, 
    8862, 8863, 8864, 8865
    };

    ifstream fp(pixelFileName.c_str());
    string line;

    for (int i = 0; i < nRuns; ++i) {
        getline(fp,line);
        singleJob(runNumbers[i], line, detectorType);

    }
}