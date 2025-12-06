import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import TranslateButton from '../../../components/TranslateButton';

export default function LayoutWrapper(props) {
  return (
    <>
      <TranslateButton />
      <Layout {...props} />
    </>
  );
}