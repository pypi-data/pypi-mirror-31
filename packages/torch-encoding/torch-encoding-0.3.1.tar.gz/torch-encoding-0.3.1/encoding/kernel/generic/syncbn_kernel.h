/*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * Created by: Hang Zhang
 * ECE Department, Rutgers University
 * Email: zhang.hang@rutgers.edu
 * Copyright (c) 2017
 *
 * This source code is licensed under the MIT-style license found in the
 * LICENSE file in the root directory of this source tree 
 *+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */
#ifndef THC_GENERIC_FILE
#define THC_GENERIC_FILE "generic/syncbn_kernel.h"
#else

void Encoding_(BatchNorm_Forward)(THCState *state, 
        THCTensor *output_, THCTensor *input_, THCTensor *xsum_,
        THCTensor *xsqsum_, THCTensor *gamma_, THCTensor *beta_,
        THCTensor *runningMean_, THCTensor *runningVar_,
        int N, double momentum, double eps, int train);

void Encoding_(BatchNorm_Backward)(THCState *state,
        THCTensor *gradoutput_, THCTensor *input_, THCTensor *gradinput_,
        THCTensor *gradgamma_, THCTensor *gradbeta_, THCTensor *xsum_,
        THCTensor *xsqsum_, THCTensor *gamma_, THCTensor *beta_,
        THCTensor *gradXsum_, THCTensor *gradXsqsum_,
        int N, double eps, int train);

void Encoding_(Sum_Square_Forward)(THCState *state, 
    THCTensor *input_, THCTensor *sum_, THCTensor *square_);

void Encoding_(Sum_Square_Backward)(THCState *state, 
    THCTensor *gradInput, THCTensor *input_, 
    THCTensor *gradSum_, THCTensor *gradSquare_);

#endif
